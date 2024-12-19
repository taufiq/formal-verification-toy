from lexer import tokens
import ply.yacc as yacc
from expr import *
from statement import *

# Modified code from PLY tutorial
# https://ply.readthedocs.io/en/latest/ply.html#ast-construction


# program : statement_list
#
# statement_list : statement
#               | statement statement_list
#
# statement : annotation
#           | assignment
#           | declaration
#           | expression
#           | assignment
#
# annotation : ANNOTATION formula
#
# assignment : ID ASSIGNMENT expression
#
#
# declaration: INT_TYPE VARIABLE
#            | BOOL_TYPE VARIABLE
#
#
# expression : expression PLUS expression                 # level = 2, left
#            | expression MINUS expression                # level = 2, left
#            | expression TIMES expression                # level = 3, left
#            | expression DIVIDE expression               # level = 3, left
#            | UMINUS expression                          # level = 4, right
#            | LPAREN expression RPAREN
#            | expression COMPARATOR expression
#            | expression BOOLEAN_OPERATOR expression
#            | ASSUME expression
#            | NUMBER
#            | VARIABLE
#            | BOOLEAN

# precedence = (
#     ('left', 'BOOLEAN_OPERATOR'),  # Logical operators
#     ('nonassoc', 'COMPARATOR'),  # Comparison operators
#     ('left', 'PLUS', 'MINUS'),  # Arithmetic operators
#     ('left', 'TIMES'),  # Multiplication
#     ('right', 'UMINUS'),  # Unary minus
# )

variables = {}
functions = {}

class ParseError(Exception):
    pass

# def p_start(p):
#     '''start : assignment
#              | expression
#              | annotation
#              | assumption
#              | declaration
#              | return_statement
#              | function_declaration'''
#     p[0] = p[1]


def p_program(p):
    '''program : statement_list'''
    p[0] = Program(p[1])

def p_statement_list(p):
    '''statement_list : statement
                    | statement statement_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]

def p_statement(p):
    '''statement : assignment
             | expression
             | annotation
             | while_loop
             | if_then_else
             | assumption
             | declaration
             | function_declaration
             | return_statement'''
    p[0] = p[1]

def p_function_declaration(p):
    'function_declaration : FUNCTION VARIABLE LPAREN parameter_list RPAREN LBRACE statement_list RBRACE'
    p[0] = FunctionDeclarationStatement(p[2], p[4], p[7])

def p_return_statement(p):
    'return_statement : RETURN expression'
    p[0] = ReturnStatement(p[2])

def p_parameter_list(p):
    '''parameter_list : declaration
                    | declaration COMMA parameter_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]

def p_while_loop(p):
    'while_loop : WHILE LPAREN expression RPAREN LBRACE statement_list RBRACE'
    condition, body = p[3], p[6]
    p[0] = WhileLoopStatement(condition, body)

def p_bool_declaration(p):
    'declaration : BOOL_TYPE VARIABLE'
    variable_name = p[2]
    if variable_name in variables:
        raise ParseError('Variable already declared')
    else:
        variables[variable_name] = DataType.BOOL
        p[0] = BooleanDeclarationStatement(variable_name)

def p_int_declaration(p):
    'declaration : INT_TYPE VARIABLE'
    variable_name = p[2]
    # if variable_name in variables:
        # raise ParseError('Variable already declared')
    # else:
    variables[variable_name] = DataType.INT
    p[0] = IntDeclarationStatement(variable_name)


def p_annotation(p):
    '''annotation : PRE_ANNOTATION expression
                  | POST_ANNOTATION expression
                  | ANNOTATION expression
                  | LOOP_ANNOTATION expression'''
    # if p[2].eval_type == "bool":
    expression = p[2]
    if p[1] == '@Pre':
        p[0] = PreAnnotationStatement(expression)
    elif p[1] == '@Post':
        p[0] = PostAnnotationStatement(expression)
    elif p[1] == '@Loop':
        p[0] = LoopAnnotationStatement(expression)
    else:
        p[0] = AnnotationStatement(expression)
    # else:
        # raise ParseError('Invalid annotation')

def p_assumption(p):
    'assumption : ASSUME expression'
    # if p[2].eval_type == "bool":
    expression = p[2]
    p[0] = AssumptionStatement(expression)
    # else:
        # raise ParseError('Invalid assumption')



def p_assignment(p):
    'assignment : VARIABLE ASSIGNMENT expression'
    variable, expression = p[1], p[3]
    if variables[variable] == DataType.INT:
        p[0] = IntAssignmentStatement(variable, expression)
    elif variables[variable] == DataType.BOOL:
        p[0] = BooleanAssignmentStatement(variable, expression)
    else:
        raise ParseError('Invalid assignment expression')

def p_expression_plus(p):
    'expression : expression PLUS expression'
    left, right = p[1], p[3]
    # if left.eval_type == DataType.INT and right.eval_type == DataType.INT:
    p[0] = IntBinaryExpression(left, right, BinaryOperator.PLUS)
    # else:
        # raise ParseError('Invalid addition expression')

def p_expression_minus(p):
    'expression : expression MINUS expression'
    left, right = p[1], p[3]
    # if left.eval_type == DataType.INT and right.eval_type == DataType.INT:
    p[0] = IntBinaryExpression(left, right, BinaryOperator.MINUS)
    # else:
        # raise ParseError('Invalid subtraction expression')

def p_expression_times(p):
    'expression : expression TIMES expression'
    left, right = p[1], p[3]
    # if left.eval_type == DataType.INT and right.eval_type == DataType.INT:
    p[0] = IntBinaryExpression(left, right, BinaryOperator.TIMES)
    # else:
        # raise ParseError('Invalid multiplication expression')

def p_parenthesis_expr(p):
    'expression : LPAREN expression RPAREN'
    p[0] = Expression(p[2])

def p_expression_num(p):
    'expression : NUMBER'
    p[0] = IntLiteralExpression(p[1])

def p_expression_bool(p):
    '''expression : TRUE
                | FALSE'''
    p[0] = BooleanLiteralExpression(p[1])


def p_expression_variable(p):
    'expression : VARIABLE'
    p[0] = VariableExpression(p[1], DataType.INT)
    # if variables.get(p[1]) == DataType.INT:
    #     p[0] = VariableExpression(p[1], DataType.INT)
    # elif variables.get(p[1]) == DataType.BOOL:
    #     p[0] = VariableExpression(p[1], DataType.BOOL)
    # else:
    #     raise ParseError('Invalid variable')

def p_expr_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    # if p[2].eval_type == "int":
    p[0] = UnaryExpression(p[2], DataType.INT)
    # else:
        # raise ParseError('Invalid unary minus expression')

def p_formula_comparison(p):
    'expression : expression COMPARATOR expression'
    left, right = p[1], p[3]
    # if p[1].eval_type == "int" and p[3].eval_type == "int":
    p[0] = ComparisonBinaryExpression(left, right, p[2])
    # else:
        # raise ParseError('Invalid comparison expression')

def p_formula_logic_op(p):
    'expression : expression BOOLEAN_OPERATOR expression'
    left, right = p[1], p[3]
    # if p[1].eval_type == "bool" and p[3].eval_type == "bool":
    p[0] = BooleanBinaryExpression(left, right, p[2])
    # else:
        # raise ParseError('Invalid boolean expression')

def p_formula_implies(p):
    'expression : expression IMPLIES expression'
    # if p[1].eval_type == "bool" and p[3].eval_type == "bool":
        # p[2] is the operator, p[1] is the left, p[3] is the right
    p[0] = ImpliesExpression(p[1], p[3])
    # else:
        # raise ParseError('Invalid implies expression')

def p_if_then_else(p):
    'if_then_else : IF LPAREN expression RPAREN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE'
    p[0] = IfThenElseStatement(p[3], p[6], p[10])
    # if p[2].eval_type == "bool":
        # p[2]=condition, p[4]=body then, p[6]=body else
        # p[0] = Node('if_then_else', None, (p[2], p[4], p[6]), None,None)
    # else:
        # raise ParseError('Invalid guard expression')


precedence = (
    ('right', 'ASSIGNMENT'),
    ('left', 'IMPLIES'),
    ('left', 'BOOLEAN_OPERATOR'),
    ('nonassoc', 'COMPARATOR'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES'),
    ('right', 'UMINUS'),  # Unary minus
)

# Error rule for syntax errors
def p_error(p):
    # print("Syntax error in input!")
    raise ParseError(f"Syntax error in input! {p}")



# Build the parser
parser = yacc.yacc(debug=True)

def gen_new_symbol(symbol):
    return symbol + ''

