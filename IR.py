import copy

from parser import *
from Node import *
from typing import Union
from project_config import DEBUG, get_debug


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

verification_conditions= []

def generate_vc(conditions, body):
    if len(conditions) != 2:
        raise PostConditionError()
    body = body[::-1]  # Reverse
    # variables = {}  # Variable -> statement
    substitutions = {}  # Variable -> New Variable
    for statement in body:  # Assume body all has assignments

        # substitute in post-cond
        if statement.symbol == "assignment":
            variable = statement.left
            rhs_expr = statement.right
            conditions[-1] = conditions[-1].subst({variable: rhs_expr})
        elif statement.symbol == "assumption":
            assumption = statement.left
            conditions[-1] = conditions[-1].add_implication(assumption)
    final_vc = conditions[-1].add_implication(conditions[0].left)
    print(final_vc.print_node_rec())
    return final_vc


def negate_expression(expression:Node):
    if expression.eval_type == "int":
        return expression
    if expression.eval_type == "bool":
        # TODO we can alternatively just add negation operator and let Z3 simplify it
        if expression.symbol == "comparison":
            if expression.op == "<":
                return Node("comparison", ">=", expression.left, expression.right, "bool")
            elif expression.op == ">":
                return Node("comparison", "<=", expression.left, expression.right, "bool")
            elif expression.op == "<=":
                return Node("comparison", ">", expression.left, expression.right, "bool")
            elif expression.op == ">=":
                return Node("comparison", "<", expression.left, expression.right, "bool")
        elif expression.symbol == "implies":
            return Node("boolean", "^", expression.left,
                        negate_expression(expression.right), "bool")
        elif expression.symbol == "boolean":
            if expression.op == "^":
                return Node("boolean", "v", negate_expression(expression.left),
                            negate_expression(expression.right), "bool")
            elif expression.op == "v":
                return Node("boolean", "^", negate_expression(expression.left),
                            negate_expression(expression.right), "bool")

def generate_basic_paths_helper(statements,conditions,body):
    last_statement_annotation = False
    last_annotation = None
    while statements:
        statement = statements.pop(0)
        statement_type = statement.symbol

        if not statement_type == "while_loop" and len(conditions) > 1:
            raise AnnotationWithNoWhileLoop

        if statement_type == "annotation":
            conditions.append(statement)
            last_statement_annotation = True
            last_annotation = statement
        elif statement_type == "assignment" or statement_type == "assumption":
            body.append(statement)
            last_statement_annotation = False
        elif statement_type == "if_then_else":
            body2 = copy.deepcopy(body)
            conditions2 = copy.deepcopy(conditions)
            statements2 = copy.deepcopy(statements)

            then_statement = statement.left[1]
            else_statement = statement.left[2]

            body.append(Node("assumption",None,statement.left[0],None, "bool"))
            body.append(then_statement)

            body2.append(Node("assumption",None,negate_expression(statement.left[0]),None, "bool"))
            body2.append(else_statement)

            generate_basic_paths_helper(statements2,conditions2,body2)
            last_statement_annotation = False
        elif statement_type == "while_loop":
            if not last_statement_annotation:
                raise WhileLoopWithNoAnnotation()
            verification_conditions.append(generate_vc(conditions, body))

            while_guard = statement.left[0]
            while_body = statement.left[1:]

            while_guard_assumption = Node("assumption",None, while_guard, None, "bool")
            not_while_guard_assumption = Node("assumption", None, negate_expression(statement.left[0]), None, "bool")

            body = [while_guard_assumption] +  while_body
            body2 = [not_while_guard_assumption]

            conditions = [last_annotation]
            conditions2 = copy.deepcopy(conditions)

            statements2 = copy.deepcopy(statements)

            generate_basic_paths_helper(statements2,conditions2,body2)

            last_statement_annotation = False
        else:
            raise Exception("Invalid expression, or expression with no effect", statement_type)
    verification_conditions.append(generate_vc(conditions,body))


def generate_basic_paths():
    with open('code.tms') as f:
        input = f.read()
        statements = parser.parse(input)

        if get_debug():
            for statement in statements:
                print(statement.print_node_rec())
            return

        # check if last statement is an annotation
        if statements[-1].symbol != "annotation":
            raise PostConditionError

        # check that nothing but variable declaration happens before the first precondition.
        # pops all declarations until an annotation is met (annotation is not popped)
        while statements:
            statement = statements[0]
            statement_type = statement.symbol
            if statement_type == "annotation":
                break
            if statement_type != "int_declaration" and statement_type != "bool_declaration" :
                raise AnnotationOrderError()
            statements.pop(0)

        conditions = []
        body = []
        generate_basic_paths_helper(statements, conditions, body)
        return verification_conditions

# generate_basic_paths()