import copy
from parser import *
from expr import *
from typing import Union, List
import z3



class AnnotationFuncError(Exception):
    def __init__(self, message="Only functions declarations are allowed, no code should exist outside a function's body."):
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
                 message="Each function should have a return statement outside any while loop and if-else statement,"
                         + " or inside both if and else bodies of an if-else statement."):
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
    elif isinstance(expression, VariableExpression):
        if expression.name in mapping:
            return mapping[expression.name]
        else:
            return expression
    elif isinstance(expression, ReturnValueVariableExpression):
        if expression.name in mapping:
            return mapping[expression.name]
        else:
            return expression
    elif isinstance(expression, BinaryExpression):
        expression.left = substitute(expression.left, mapping)
        expression.right = substitute(expression.right, mapping)
        return expression
    elif isinstance(expression, UnaryExpression):
        expression.expression = substitute(expression.expression, mapping)
        return expression


total = []

def collector(statements:List[Statement], path:List[Statement], context:Union[None, Context]):
    statements = copy.deepcopy(statements)
    path = copy.deepcopy(path)

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

        collector(then_statements + tail, path + [condition_holds], Context(context.pre_condition, context.post_condition, statement))


        collector(else_statements + tail, path + [condition_doesnt_hold], Context(context.pre_condition, context.post_condition, statement))

    elif isinstance(statement, WhileLoopStatement):
        invariant = statement.invariant

        path.append(invariant)
        total.append(copy.deepcopy(path))

        # Keep Invariant
        path = [path[-1]]

        condition_holds = AssumptionStatement(statement.condition)
        condition_doesnt_hold = AssumptionStatement(NotExpression(statement.condition))

        collector(statement.body, path + [condition_holds], Context(context.pre_condition, context.post_condition, statement))

        collector(tail, path + [condition_doesnt_hold], Context(context.pre_condition, context.post_condition, statement))

    elif isinstance(statement, ReturnStatement):
        path.append(statement)
        path.append(context.post_condition)
        total.append(copy.deepcopy(path))


    elif isinstance(statement, AssignmentStatement) or isinstance(statement, AssumptionStatement):
        path.append(statement)
        collector(tail, path, context)

    elif isinstance(statement, AnnotationStatement):
        raise AnnotationWithNoWhileLoop()

    elif isinstance(statement, DeclarationStatement):
        collector(tail, path, context)
    else:
        raise ExpressionWithNoEffect()

    return


def convert_to_z3(basic_paths, function:FunctionDeclarationStatement) -> bool:
    basic_paths = copy.deepcopy(basic_paths)
    is_invalid = False

    print("Validating function: " + function.function_name)
    for basic_path in basic_paths:

        pre, post = basic_path[0], basic_path[-1]
        variables = get_functions(function.function_name)[0]
        # variables = functions[function.function_name][0]

        if isinstance(basic_path[-2], ReturnStatement):
            if isinstance(function, IntFunctionDeclarationStatement):
                basic_path[-2] = IntAssignmentStatement("rv", basic_path[-2].expression)
                variables["rv"] = DataType.INT
            elif isinstance(function, BoolFunctionDeclarationStatement):
                basic_path[-2] = BooleanAssignmentStatement("rv", basic_path[-2].expression)
                variables["rv"] = DataType.BOOL

        statements = basic_path[1:-1]

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
                post = ImpliesExpression(statement.expression, post, "=>")

            if isinstance(statement, AnnotationStatement):
                pass

        mapping['z3'] = z3
        fol_statement_z3 = f"z3.Implies({Z3Serializer.serialize(pre)}, {Z3Serializer.serialize(post)})"
        fol_statement = f"({pre}) => ({post})"
        solver.add(z3.Not(eval(fol_statement_z3, mapping)))
        solver_result = solver.check()
        print("Original basic path")
        print(immutable_basic_path)
        print("VC")
        print(fol_statement)
        if solver_result == z3.sat:
            is_invalid = True
            counter_example = solver.model()
            print("Invalid!")
            print("Counter example: ",counter_example)
        else:
            print("Valid!")
    return not is_invalid

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

def ensure_function_declarations(statements):
    ''' make sure that all the code is inside a function's body  with pre and post annotations '''

    for statement in statements:
        if isinstance(statement, FunctionDeclarationStatement):
            continue
        else:
            raise AnnotationFuncError()


    for function in statements:
        statement_index = 0
        body_statements = function.body
        while statement_index < len(body_statements):
            if isinstance(body_statements[statement_index], DeclarationStatement):
                statement_index += 1
            else:
                break

        if statement_index < len(body_statements):
            if isinstance(body_statements[statement_index], PreAnnotationStatement):
                if isinstance(body_statements[statement_index+1], PostAnnotationStatement):
                    statement_index = statement_index + 2
                    while statement_index < len(body_statements):
                        if isinstance(statement_index, PreAnnotationStatement):
                            raise PreConditionError("Incorrect placement of Precondition")
                        if isinstance(statement_index, PostAnnotationStatement):
                            raise PostConditionError("Incorrect placement of PostCondition")
                        statement_index = statement_index + 1
                else:
                    raise PostConditionMissing()
            else:
                raise PreConditionError("Missing precondition")

    return



def ensure_return_statements(program_statements) -> None:
    '''ensure correct return statements types and placement.'''

    def ensure_correct_return_types(function: FunctionDeclarationStatement, statements) -> None:
        '''make sure that the type of the expressions returned by all return statements
         match the function type.'''

        for statement in statements:
            if isinstance(statement, ReturnStatement):
                function.assert_valid_return_statement(statement)
            elif isinstance(statement, IfThenElseStatement):
                ensure_correct_return_types(function, statement.then_body)
                ensure_correct_return_types(function, statement.else_body)
            elif isinstance(statement, WhileLoopStatement):
                ensure_correct_return_types(function, statement.body)

    def ensure_return_statements_aux(statements) -> bool:
        '''
        Every function should have at least 1 return statement outside any if-else or while loop statements.
        '''
        for statement in statements:
            if isinstance(statement, ReturnStatement):
                return True
            elif isinstance(statement, IfThenElseStatement):
                if (ensure_return_statements_aux(statement.then_body)
                        and ensure_return_statements_aux(statement.else_body)):
                    return True
        return False

    for statement in program_statements:
        if isinstance(statement, FunctionDeclarationStatement):
            ensure_correct_return_types(statement, statement.body)
            if not ensure_return_statements_aux(statement.body):
                raise MissingReturnStatement()


def ensure_pre_post_condition(pre_condition:AnnotationStatement, post_condition:AnnotationStatement, parameter_list:List[DeclarationStatement]):
    ''' make sure that the precondition and postcondition contain only parameter variables, or also "rv" for postcondition '''
    def ensure_pre_post_condition_aux(expression, parameter_list, condition: str):
        assert (condition == "precondition" or condition == "postcondition")

        if expression is None:
            return True
        elif isinstance(expression, IntLiteralExpression) or isinstance(expression, BooleanLiteralExpression):
            return True
        elif isinstance(expression, ReturnValueVariableExpression):
            if condition == "precondition":
                return False
            elif condition == "postcondition":
                return True
        elif isinstance(expression, VariableExpression):
            return expression.name in parameter_list
        elif isinstance(expression, BinaryExpression):
            return ensure_pre_post_condition_aux(expression.left, parameter_list, condition) and \
                ensure_pre_post_condition_aux(expression.right, parameter_list, condition)
        elif isinstance(expression, UnaryExpression):
            return ensure_pre_post_condition_aux(expression.expression, parameter_list, condition)

    parameter_list = [parameter.variable for parameter in parameter_list]

    if not ensure_pre_post_condition_aux(pre_condition.expression, parameter_list, "precondition"):
        raise PreConditionError()
    if not ensure_pre_post_condition_aux(post_condition.expression, parameter_list, "postcondition"):
        raise PostConditionError()



def generate_basic_paths(file_path:str) -> bool:
    global total

    with open(file_path) as f:
        input = f.read()
        program = parser.parse(input)
        statements = program.statements

        ensure_function_declarations(statements)

        ensure_and_attach_loop_annotation(statements)

        ensure_return_statements(statements)


        is_invalid = False
        for func_index in range(0,len(statements)):

            function = statements[func_index]
            function.set_precondition()
            function.set_postcondition()

            pre_condition = function.precondition
            post_condition = function.postcondition

            assert(isinstance(statements[func_index], FunctionDeclarationStatement))
            assert(isinstance(pre_condition, PreAnnotationStatement))
            assert(isinstance(post_condition, PostAnnotationStatement))

            ensure_pre_post_condition(pre_condition, post_condition, function.parameter_list)

            collector(function.get_body_after_annotations(),[pre_condition],Context(pre_condition,post_condition,None))
            # basic_paths.extend(total)
            if not(convert_to_z3(total,function)):
                is_invalid = True
            total = []

        return not is_invalid


def print_paths(all_paths):
    for path in all_paths:
        print("\n".join(map(str, path)))
        print("-"*100)
# generate_basic_paths()
