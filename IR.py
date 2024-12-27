import copy
from parser import *
from expr import *
from typing import Union
from project_config import DEBUG, get_debug
import z3


class AnnotationOrderError(Exception):
    def __init__(self, message="Only variable declarations can precede the first annotation."):
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

# Function that collects all paths for a while loop
# def while_loop_collector(while_loop_statement, path=[], pre=None, post=None, context=None):



def collector(statements, path=[], pre=None, post=None, context=None):
    if statements == []:
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
        then_flow = collector(then_statements, path, pre, post, statement)
        path.pop()

        path.append(condition_doesnt_hold)
        else_flow = collector(else_statements, path, pre, post, statement)
        path.pop()

    elif isinstance(statement, WhileLoopStatement):
        invariant = statement.invariant

        path.append(invariant)
        total.append(copy.deepcopy(path))

        # Keep Invariant
        path = [path[-1]]

        condition_holds_assumption = AssumptionStatement(statement.condition)
        condition_doesnt_hold_assumption = AssumptionStatement(NotExpression(statement.condition))

        condition_holds = AssumptionStatement(statement.condition)
        condition_doesnt_hold = AssumptionStatement(NotExpression(statement.condition))

        path.append(condition_holds)
        while_flow = collector(statement.body, path, pre, post, statement)
        path.pop()

        path.append(condition_doesnt_hold)
        while_flow = collector(tail, path, pre, post, statement)
        path.pop()
    elif isinstance(statement, AnnotationStatement):
        path.append(statement)
        collector(tail, path, pre, post, context)
        path.pop()
    else:
        path.append(statement)
        collector(tail, path, pre, post, context)
        path.pop()
    return path

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

def generate_basic_paths():
    global total
    with open('test.tms') as f:
        input = f.read()
        program = parser.parse(input)
        statements = program.statements

        # check that nothing but variable declaration happens before the first precondition.
        # pops all declarations until an annotation is met (annotation is not popped)
        for statement in statements:
            if isinstance(statement, AnnotationStatement):
                break
            if not isinstance(statement, DeclarationStatement):
                raise AnnotationOrderError()
        
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
        for statement in statements:
            if accumulator == []:
                # Check that the first statement is a pre-annotation
                if not isinstance(statement, PreAnnotationStatement):
                    raise AnnotationOrderError()
                else:
                    accumulator.append(statement)
            else:
                # Check that the last statement is a pre-annotation
                if isinstance(accumulator[-1], PreAnnotationStatement):
                    if isinstance(statement, PostAnnotationStatement):
                        accumulator.append(statement)
                    else:
                        raise AnnotationOrderError()
                elif isinstance(accumulator[-1], PostAnnotationStatement):
                    if not isinstance(statement, FunctionDeclarationStatement):
                        raise AnnotationOrderError()
                    else:
                        accumulator.append(statement)
                        blocks.append(accumulator)
                        accumulator = []
        conditions = []
        body = []
        verification_conditions = []
        for block in blocks:
            pre_condition, post_condition, function = block
            statements = [pre_condition] + function.body + [post_condition]
            collector(statements)
            verification_conditions.extend(total)
            convert_to_z3(verification_conditions)
            total = []

        return []


def print_paths(all_paths):
    for path in all_paths:
        print("\n".join(map(str, path)))
        print("-"*100)
# generate_basic_paths()
