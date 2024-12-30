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

class PostConditionMissing(Exception):
    def __init__(self, message="Post condition missing."):
        super().__init__(message)

class PreConditionError(Exception):
    def __init__(self, message="Invalid Precondition."):
        super().__init__(message)

class PostConditionError(Exception):
    def __init__(self, message="Invalid Post condition."):
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

class MissingReturnStatement(Exception):
    def __init__(self,
                 message="Each function should have a return statement outside if/else statements and while loops."):
        super().__init__(message)

class Context:
    def __init__(self, pre_condition:AnnotationStatement, post_condition:AnnotationStatement,
                 origin_statement:Union[None,Statement]):
        self.pre_condition = pre_condition
        self.post_condition = post_condition
        self.origin_statement = origin_statement



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

def collector(statements:List[Statement], path:List[Statement], context:Union[None, Context]):
    statements = copy.copy(statements)
    path = copy.copy(path)

    if not statements:
        if context.origin_statement and isinstance(context.origin_statement, WhileLoopStatement):
            path.append(context.origin_statement.invariant)
        else:
            path.append(context.post_condition)
        path = copy.deepcopy(path)
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
        collector(then_statements + tail, path, Context(context.pre_condition, context.post_condition, statement))


        path.append(condition_doesnt_hold)
        collector(else_statements + tail, path, Context(context.pre_condition, context.post_condition, statement))

    elif isinstance(statement, WhileLoopStatement):
        invariant = statement.invariant

        path.append(invariant)
        total.append(copy.deepcopy(path))

        # Keep Invariant
        path = [path[-1]]

        condition_holds = AssumptionStatement(statement.condition)
        condition_doesnt_hold = AssumptionStatement(NotExpression(statement.condition))

        path.append(condition_holds)
        collector(statement.body, path, Context(context.pre_condition, context.post_condition, statement))

        path.append(condition_doesnt_hold)
        collector(tail, path, Context(context.pre_condition, context.post_condition, statement))

    elif isinstance(statement, ReturnStatement):
        path.append(statement)
        path.append(context.post_condition)
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
        else:
            explore_and_collect_variables(statement.expression, variables)
    return list(variables.keys())


def convert_to_z3(basic_paths, function:FunctionDeclarationStatement):
    basic_paths = copy.deepcopy(basic_paths)
    for basic_path in basic_paths:

        pre, post = basic_path[0], basic_path[-1]
        variables = functions[function.function_name]
        statements = basic_path[1:-1]

        if isinstance(basic_path[-2], ReturnStatement):
            if isinstance(function, IntFunctionDeclarationStatement):
                basic_path[-2] = IntAssignmentStatement("rv", basic_path[-2].expression)
                variables["rv"] = DataType.INT
            elif isinstance(function, BoolFunctionDeclarationStatement):
                basic_path[-2] = BooleanAssignmentStatement("rv", basic_path[-2].expression)
                variables["rv"] = DataType.BOOL

        immutable_basic_path = copy.deepcopy(basic_path)
        pre = pre.expression
        post = post.expression

        mapping = {}
        solver = z3.Solver()

        for variable in variables.keys():
            if variables[variable] == DataType.INT:
                mapping[variable] = z3.Int(variable)
            elif variables[variable] == DataType.BOOL:
                mapping[variable] = z3.Bool(variable)

        for statement in statements[::-1]:
            if isinstance(statement, AssignmentStatement):
                variable_name = statement.variable
                # Side effect that affects post condition
                # Back propgation
                substitute(post, { variable_name: statement.expression })
            elif isinstance(statement, AssumptionStatement):
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
    i = 0
    while i < len(statements):
        statement = statements[i]
        if isinstance(statement, WhileLoopStatement):
            if not isinstance(statements[i-1], LoopAnnotationStatement):
                raise LoopAnnotationError()
            else:
                statements[i].invariant = statements[i-1]
                statements.pop(i - 1)
                i = i - 1
        if isinstance(statement, FunctionDeclarationStatement):
            ensure_and_attach_loop_annotation(statement.body)
        if isinstance(statement, IfThenElseStatement):
            ensure_and_attach_loop_annotation(statement.then_body)
            ensure_and_attach_loop_annotation(statement.else_body)
        i += 1

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



def ensure_return_statements(statements):
    '''make sure that the type of the expressions returned match the function type
     works for nested function calls'''

    def ensure_return_statements_aux(function: FunctionDeclarationStatement):
        '''
        Every function should have at least 1 return statement outside any if-else or while loop statements.
        '''
        for func_statement in function.body:
            if isinstance(func_statement, ReturnStatement):
                return function.check_valid_return_statement(func_statement)
            elif isinstance(func_statement, FunctionDeclarationStatement):
                ensure_return_statements_aux(func_statement)
        return False

    for statement in statements:
        if isinstance(statement, FunctionDeclarationStatement):
            if not ensure_return_statements_aux(statement):
                raise MissingReturnStatement()


def ensure_pre_post_condition(pre_condition:AnnotationStatement, post_condition:AnnotationStatement, parameter_variables:List[DeclarationStatement]):
    ''' make sure that the precondition and postcondition contain only parameter variables, or also "rv" for postcondition '''
    def ensure_pre_post_condition_aux(expression, parameter_variables, condition: str):
        assert (condition == "precondition" or condition == "postcondition")

        if expression is None:
            return True
        elif isinstance(expression, ReturnValueVariableExpression):
            if condition == "precondition":
                return False
            elif condition == "postcondition":
                return True
        elif isinstance(expression, VariableExpression):
            return expression.name in parameter_variables
        elif isinstance(expression, BinaryExpression):
            return explore_and_collect_variables(expression.left, parameter_variables) and \
                explore_and_collect_variables(expression.right, parameter_variables)
        elif isinstance(expression, UnaryExpression):
            return explore_and_collect_variables(expression.expression, parameter_variables)

    parameter_variables = [parameter.variable for parameter in parameter_variables]

    if not ensure_pre_post_condition_aux(pre_condition, parameter_variables, "precondition"):
        raise PreConditionError()
    if not ensure_pre_post_condition_aux(post_condition, parameter_variables, "postcondition"):
        raise PostConditionError()


def generate_basic_paths():
    global total
    with open('test.tms') as f:
        input = f.read()
        program = parser.parse(input)
        statements = program.statements

        ensure_function_declarations(statements)

        ensure_and_attach_loop_annotation(statements)

        ensure_return_statements(statements)


        basic_paths = []

        for func_index in range(0,len(statements),3):
            assert(isinstance(statements[func_index], PreAnnotationStatement))
            assert(isinstance(statements[func_index + 1], PostAnnotationStatement))
            assert(isinstance(statements[func_index + 2], FunctionDeclarationStatement))

            pre_condition = statements[func_index]
            post_condition = statements[func_index + 1]
            function = statements[func_index + 2]

            ensure_pre_post_condition(pre_condition, post_condition, function.parameter_variables)

            # statements = function.body
            collector(function.body,[pre_condition],Context(pre_condition,post_condition,None))
            basic_paths.extend(total)
            convert_to_z3(basic_paths,function)
            total = []

        return


def print_paths(all_paths):
    for path in all_paths:
        print("\n".join(map(str, path)))
        print("-"*100)
# generate_basic_paths()
