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



def generate_basic_paths_rec(statements, path, function_type, pre=Union[None,List[Statement]], post=Union[None,List[Statement]], context=None):

    if pre is not None:
        path = copy.copy(pre)

    basic_paths = []

    while statements:
        statement = statements.pop()

        if isinstance(statement, IfThenElseStatement):
            then_statements = statement.then_body
            else_statements = statement.else_body

            condition_holds = AssumptionStatement(statement.condition)
            condition_doesnt_hold = AssumptionStatement(NotExpression(statement.condition))

            basic_paths += generate_basic_paths_rec(copy.copy(then_statements + statements), path +  [condition_holds],
                                                    function_type, None, None, context)
            path = path + [condition_doesnt_hold]

            statements = copy.copy(else_statements + statements)

        elif isinstance(statement, WhileLoopStatement):

            invariant = statement.invariant
            path.append(invariant)

            basic_paths += path

            condition_holds = AssumptionStatement(statement.condition)
            condition_doesnt_hold = AssumptionStatement(NotExpression(statement.condition))

            path = [invariant, condition_doesnt_hold]
            basic_paths += generate_basic_paths_rec(copy.copy(statement.body), [], function_type,
                                                    copy.copy([invariant, condition_holds]), invariant, context)

        elif isinstance(statement, ReturnStatement):
            path.append(statement)
            break

        elif isinstance(statement, AssignmentStatement) or isinstance(statement, AssumptionStatement):
            path.append(statement)

        elif isinstance(statement, AnnotationStatement):
            raise AnnotationWithNoWhileLoop()

        else:
            raise ExpressionWithNoEffect


    if post is not None:
        path = copy.copy(path + post)

    basic_paths.append(path)

    return basic_paths

def basic_path_generator(block, path=[]):
    pre, post, function_declaration = block
    pre = pre.expression
    post = post.expression
    parameters = function_declaration.parameter_list
    body_statements = function_declaration.body
    path = copy.deepcopy(path)

   
    return []

def convert_to_z3(block):
    pre, post, function_declaration = block
    pre = pre.expression
    post = post.expression
    parameters = function_declaration.parameter_list
    body = function_declaration.body
    mapping = {}
    solver = z3.Solver()
    for parameter in parameters:
        mapping[parameter.variable] = z3.Int(parameter.variable)
    for statement in body[::-1]:
        if isinstance(statement, AssignmentStatement):
            variable_name = statement.variable
            # Side effect that affects post condition
            # Back propgation
            substitute(post, { variable_name: statement.expression })
    mapping['z3'] = z3
    solver.add(z3.Not(eval(f"z3.Implies({Z3Serializer.serialize(pre)}, {Z3Serializer.serialize(post)})", mapping)))
    solver_result = solver.check()
    print(f"Function ({function_declaration.function_name}): ", end="")
    if solver_result == z3.sat:
        counter_example = solver.model()
        print("Invalid!")
        print("Counter example: ",counter_example)
    else:
        print("Valid!")
    return pre, post, body, mapping

# check that every while loop is preceded with a while loop annotation
# remove the invariant from the list of statements and add it in the invariant field
# of the while loop statement.
def ensure_and_attach_loop_annotation(statements):
    for i in range(len(statements)):
        statement = statements[i]
        if isinstance(statement, WhileLoopStatement):
            if not isinstance(statements[i-1], LoopAnnotationStatement):
                raise LoopAnnotationError()
            else:
                statements[i].invariant = statements[i-1]
                statements.pop(i-1)
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

        for i in range(len(statements)):
            statement = statements[i]
            if isinstance(statement, WhileLoopStatement):
                if isinstance(statements[i-1], LoopAnnotationStatement):
                    statements[i].invariant = statements[i-1]
                else:
                    raise LoopAnnotationError()
        
        ensure_and_attach_loop_annotation(statements)

        blocks = []
        accumulator = []
        conditions = []
        body = []
        verification_conditions = []

        for func_index in range(0,len(statements),3):
            assert(isinstance(statements[func_index], PreAnnotationStatement))
            assert(isinstance(statements[func_index + 1], PostAnnotationStatement))
            assert(isinstance(statements[func_index + 2], FunctionDeclarationStatement))

            pre = statements[func_index]
            post = statements[func_index + 1]
            func = statements[func_index + 2]

            if isinstance(func, IntFunctionDeclarationStatement):
                generate_basic_paths_rec(copy.copy(func.body), [], "INT", pre, post, func.parameter_list)
            elif isinstance(func, BoolFunctionDeclarationStatement):
                generate_basic_paths_rec(copy.copy(func.body), [], "BOOL", pre, post, func.parameter_list)





        #
        #
        # for block in blocks:
        #     collector(block[2].body)
        #     verification_conditions.extend(total)
        #     # convert_to_z3(block)
        #     total = []

        return []


def print_paths(all_paths):
    for path in all_paths:
        print("\n".join(map(str, path)))
        print("-"*100)
# generate_basic_paths()
