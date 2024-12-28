import copy
from parser import *
from expr import *
from typing import Union, List
from project_config import DEBUG, get_debug
import z3


class AnnotationFuncError(Exception):
    def __init__(self, message="Only functions declarations are allowed, no code should exist outside functions' body."):
        super().__init__(message)

class AnnotationOrderError(Exception):
    def __init__(self, message="A precondition should be followed by a postcondition for each function."):
        super().__init__(message)

class PostConditionError(Exception):
    def __init__(self, message="Post condition required."):
        super().__init__(message)

class AnnotationWithNoWhileLoop(Exception):
    def __init__(self, message="Annotation with no while loop following it."):
        super().__init__(message)

class WhileLoopWithNoAnnotation(Exception):
    def __init__(self, message="While loop without annotation."):
        super().__init__(message)

class LoopAnnotationError(Exception):
    def __init__(self, message="Loop annotation without a while loop following it."):
        super().__init__(message)

class ExpressionWithNoEffect(Exception):
    def __init__(self, message="Expression with no effect."):
        super().__init__(message)

def substitute(expression, mapping):
    if isinstance(expression, LiteralExpression):
        return expression
    if isinstance(expression, VariableExpression):
        if expression.name in mapping:
            return mapping[expression.name]
        else:
            return expression
    else:
        expression.left = substitute(expression.left, mapping)
        expression.right = substitute(expression.right, mapping)
        return expression


total = []

def generate_basic_paths_rec(statements, path, function_type, pre=Union[None,List[Statement]], post=Union[None,List[Statement]], context=None):

    if pre is not None:
        path = copy.copy(pre)

    basic_paths = []

    while statements:
        statement = statements.pop()

        if isinstance(statement, IfThenElseStatement):
            then_statements = statement.then_body
            else_statements = statement.else_body


def collector(statements, path=[], context=None):
    statements = copy.copy(statements)
    path = copy.copy(path)

    if not statements:
        path = copy.deepcopy(path)
        if isinstance(context, WhileLoopStatement):
            path.append(context.invariant)
        total.append(path)
        return

    statement = statements[0]
    tail = statements[1:]

    if isinstance(statement, IfThenElseStatement):
        then_statements = statement.then_body
        else_statements = statement.else_body

        condition_holds = AssumptionStatement(statement.condition)
        condition_doesnt_hold = AssumptionStatement(NotExpression(statement.condition))

        path.append(condition_holds)
        collector(then_statements + tail, path, statement)


        path.append(condition_doesnt_hold)
        collector(else_statements + tail, path, statement)

    elif isinstance(statement, WhileLoopStatement):
        invariant = statement.invariant

        path.append(invariant)
        total.append(copy.deepcopy(path))

        # Keep Invariant
        path = [path[-1]]

        condition_holds = AssumptionStatement(statement.condition)
        condition_doesnt_hold = AssumptionStatement(NotExpression(statement.condition))

        path.append(condition_holds)
        collector(statement.body, path, statement)

        path.append(condition_doesnt_hold)
        collector(tail, path, statement)

    elif isinstance(statement, ReturnStatement):
        path.append(statement)
        total.append(copy.deepcopy(path))

    elif isinstance(statement, AssignmentStatement) or isinstance(statement, AssumptionStatement):
        path.append(statement)
        collector(tail, path, context)

    elif isinstance(statement, AnnotationStatement):
        raise AnnotationWithNoWhileLoop()

    else:
        raise ExpressionWithNoEffect()

    return


# This goes through all statements and sees what variables there are
# Assumes all variables are Integers
def collect_variables(statements):
    variables = {}
    for statement in statements:
        if isinstance(statement, AssignmentStatement):
            variables[statement.variable] = statement.expression
            # TODO: add deduction?
        else:
            explore_and_collect_variables(statement.expression, variables)
    return list(variables.keys())


def convert_to_z3(basic_paths):
    basic_paths = copy.deepcopy(basic_paths)
    for basic_path in basic_paths:
        pre, post = basic_path[0], basic_path[-1]
        immutable_basic_path = copy.deepcopy(basic_path)
        statements = basic_path[1:-1]
        pre = pre.expression
        post = post.expression
        variables = collect_variables(basic_path)
        mapping = {}
        solver = z3.Solver()
        for variable in variables:
            mapping[variable] = z3.Int(variable)
        for statement in statements[::-1]:
            if isinstance(statement, AssignmentStatement):
                variable_name = statement.variable
                # Side effect that affects post condition
                # Back propgation
                substitute(post, { variable_name: statement.expression })
            if isinstance(statement, AssumptionStatement):
                post = ImpliesBinaryExpression(statement.expression, post)
            if isinstance(statement, AnnotationStatement):
                pass

        mapping['z3'] = z3
        fol_statement = f"z3.Implies({Z3Serializer.serialize(pre)}, {Z3Serializer.serialize(post)})"
        solver.add(z3.Not(eval(fol_statement, mapping)))
        solver_result = solver.check()
        print("Original basic path")
        print(immutable_basic_path)
        print("FOL")
        print(fol_statement)
        if solver_result == z3.sat:
            counter_example = solver.model()
            print("Invalid!")
            print("Counter example: ",counter_example)
        else:
            print("Valid!")

def ensure_and_attach_loop_annotation(statements):
    '''This takes the loop annotation and merges it into
        the while loop statement'''
    for i in range(len(statements)):
        statement = statements[i]
        if isinstance(statement, WhileLoopStatement):
            if not isinstance(statements[i-1], LoopAnnotationStatement):
                raise LoopAnnotationError()
            else:
                statements[i].invariant = statements[i-1]
                statements.pop(i - 1)
        if isinstance(statement, FunctionDeclarationStatement):
            ensure_and_attach_loop_annotation(statement.body)
        if isinstance(statement, IfThenElseStatement):
            ensure_and_attach_loop_annotation(statement.then_body)
            ensure_and_attach_loop_annotation(statement.else_body)

# make sure that all the code is inside function declarations with pre and post annotations
def ensure_function_declarations(statements):
    previous_statement = None

    class StatementType(Enum):
        PRE = 1
        POST = 2
        FUNC = 3

    if len(statements) % len(StatementType) != 0:
        raise AnnotationFuncError()

    for statement in statements:
        if isinstance(statement, PreAnnotationStatement):
            if  not (previous_statement is None or previous_statement == StatementType.FUNC):
                raise AnnotationOrderError()
            else:
                previous_statement = StatementType.PRE
        elif isinstance(statement, PostAnnotationStatement):
            if previous_statement != StatementType.PRE:
                raise AnnotationOrderError()
            else:
                previous_statement = StatementType.POST
        elif isinstance(statement, FunctionDeclarationStatement):
            if previous_statement != StatementType.POST:
                raise AnnotationOrderError()
            else:
                previous_statement = StatementType.FUNC
        else:
            raise AnnotationFuncError()

# Every function should have at least 1 return statement outside any if-else or while loop statements.
def ensure_return_statements_aux(function:FunctionDeclarationStatement):
    for statement in function.body:
        if isinstance(statement, ReturnStatement):
            return function.check_valid_return_statement(statement)
        elif isinstance(statement, FunctionDeclarationStatement):
            ensure_return_statements_aux(statement)
    return False

# make sure that the type of the expressions returned match the function type
# works for nested function calls
def ensure_return_statements(statements):
    for statement in statements:
        if isinstance(statement, FunctionDeclarationStatement):
            ensure_return_statements(statement.body)

def generate_basic_paths():
    global total
    with open('test.tms') as f:
        input = f.read()
        program = parser.parse(input)
        statements = program.statements

        ensure_function_declarations(statements)

        ensure_and_attach_loop_annotation(statements)

        ensure_return_statements(statements)

        verification_conditions = []

        for func_index in range(0,len(statements),3):
            assert(isinstance(statements[func_index], PreAnnotationStatement))
            assert(isinstance(statements[func_index + 1], PostAnnotationStatement))
            assert(isinstance(statements[func_index + 2], FunctionDeclarationStatement))

            pre_condition = statements[func_index]
            post_condition = statements[func_index + 1]
            function = statements[func_index + 2]

            statements = [pre_condition] + function.body + [post_condition]
            collector(statements)
            verification_conditions.extend(total)
            convert_to_z3(verification_conditions)
            total = []

        return


def print_paths(all_paths):
    for path in all_paths:
        print("\n".join(map(str, path)))
        print("-"*100)
# generate_basic_paths()
