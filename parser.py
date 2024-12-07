from lexer import tokens
import ply.yacc as yacc
from Node import Node

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
    p[0] = p[1]

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
             | assumption
             | declaration'''
    p[0] = p[1]


def p_bool_declaration(p):
    'declaration : BOOL_TYPE VARIABLE'
    if p[2] in variables:
        raise ParseError('Variable already declared')
    else:
        variables[p[2]] = "BOOL"
        p[0] = Node("bool_declaration",None,p[2],None, "bool")

def p_int_declaration(p):
    'declaration : INT_TYPE VARIABLE'
    if p[2] in variables:
        raise ParseError('Variable already declared')
    else:
        variables[p[2]] = "INT"
        p[0] = Node("int_declaration",None,p[2],None, "int")


def p_annotation(p):
    'annotation : ANNOTATION expression'
    if p[2].eval_type == "bool":
        p[0] = Node('annotation',p[1], p[2], None, "bool")
    else:
        raise ParseError('Invalid annotation')

def p_assumption(p):
    'assumption : ASSUME expression'
    if p[2].eval_type == "bool":
        p[0] = Node('assumption',p[1], p[2], None, "bool")
    else:
        raise ParseError('Invalid assumption')



def p_assignment(p):
    'assignment : VARIABLE ASSIGNMENT expression'
    if variables[p[1]] == "INT" and p[3].eval_type == "int":
        p[0] = Node('assignment',  p[2], p[1], p[3],"int")
    elif variables[p[1]] == "BOOL" and p[3].eval_type == "bool":
        p[0] = Node('assignment',  p[2], p[1], p[3],"bool")
    else:
        raise ParseError('Invalid assignment expression')

def p_expression_plus(p):
    'expression : expression PLUS expression'
    if p[1].eval_type == "int" and p[3].eval_type == "int":
        p[0] = Node('plus', p[2], p[1], p[3], "int")
    else:
        raise ParseError('Invalid addition expression')

def p_expression_minus(p):
    'expression : expression MINUS expression'
    if p[1].eval_type == "int" and p[3].eval_type == "int":
        p[0] = Node('minus', p[2], p[1], p[3], "int")
    else:
        raise ParseError('Invalid subtraction expression')

def p_expression_times(p):
    'expression : expression TIMES expression'
    if p[1].eval_type == "int" and p[3].eval_type == "int":
        p[0] = Node('times', p[2], p[1], p[3], "int")
    else:
        raise ParseError('Invalid multiplication expression')

def p_parenthesis_expr(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_num(p):
    'expression : NUMBER'
    p[0] = Node('NUMBER',None, p[1], None, "int")

def p_expression_bool(p):
    '''expression : TRUE
                | FALSE'''
    p[0] = Node('BOOLEAN',None, p[1], None, "bool")


def p_expression_variable(p):
    'expression : VARIABLE'
    if variables.get(p[1]) == "INT":
        p[0] = Node('variables', None, p[1], None, "int")
    elif variables.get(p[1]) == "BOOL":
        p[0] = Node('variables', None, p[1], None, "bool")
    else:
        raise ParseError('Invalid variable')

def p_expr_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    if p[2].eval_type == "int":
        p[0] = Node("unary minus",p[1],-p[2],None,"int")
    else:
        raise ParseError('Invalid unary minus expression')

def p_formula_comparison(p):
    'expression : expression COMPARATOR expression'
    if p[1].eval_type == "int" and p[3].eval_type == "int":
        p[0] = Node('comparison', p[2], p[1], p[3],"bool")
    else:
        raise ParseError('Invalid comparison expression')

def p_formula_logic_op(p):
    'expression : expression BOOLEAN_OPERATOR expression'
    if p[1].eval_type == "bool" and p[3].eval_type == "bool":
        p[0] = Node('boolean', p[2], p[1], p[3], "bool")
    else:
        raise ParseError('Invalid boolean expression')

def p_formula_implies(p):
    'expression : expression IMPLIES expression'
    if p[1].eval_type == "bool" and p[3].eval_type == "bool":
        # p[2] is the operator, p[1] is the left, p[3] is the right
        p[0] = Node('implies', p[2], p[1], p[3],"bool")
    else:
        raise ParseError('Invalid implies expression')

def p_if_then_else(p):
    'expression : IF expression THEN assignment ELSE assignment'
    if p[2].eval_type == "bool":
        # p[2]=condition, p[4]=body then, p[6]=body else
        p[0] = Node('if_then_else', None, (p[2], p[4], p[6]), None,None)
    else:
        raise ParseError('Invalid guard expression')

def p_while_loop(p):
    'expression : WHILE LPAREN expression RPAREN LBRACE statement_list RBRACE'
    if p[3].eval_type != "bool":
        raise ParseError('Invalid while loop')
    p[0] = Node("while_loop", None, [p[3]] +  p[6], None,None)



#
# def p_function_declaration(p):
#     '''function_declaration : FUNCTION VARIABLE LPAREN parameter_list RPAREN LBRACE expression_list RBRACE'''
#     functions[p[2]] = {'params': p[4], 'body': p[7]}
#
# def p_parameter_list(p):
#     '''parameter_list : declaration
#                       | declaration COMMA parameter_list
#                       '''
#
#     if len(p) == 2:
#         Node("parameter_list",None,[p[1]],None,None)
#     else:
#         Node("parameter_list",None,[p[1]] + p[3],None,None)


# def p_expression_list(p):
#     '''expression_list : expression
#                       | expression expression_list
#                       | empty'''
#     if len(p) == 2:
#         p[0] = [p[1]]
#     else:
#         p[0] = [p[1]] + p[2]
#
# def p_return_statement(p):
#     'return_statement : RETURN expression'
#     p[0] = ('return', p[2])
#
# def p_empty(p):
#     '''empty :'''
#     p[0] = None


precedence = (
    ('left', 'BOOLEAN_OPERATOR'),
    ('nonassoc', 'COMPARATOR'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES'),
    ('right', 'UMINUS'),
)

# Error rule for syntax errors
def p_error(p):
    # print("Syntax error in input!")
    raise ParseError("Syntax error in input!")



# Build the parser
parser = yacc.yacc(debug=True)

def gen_new_symbol(symbol):
    return symbol + ''

