from lexer import tokens
import ply.yacc as yacc
from Node import Node

# Modified code from PLY tutorial
# https://ply.readthedocs.io/en/latest/ply.html#ast-construction

# annotation : ANNOTATION formula
#
# assignment : ID ASSIGNMENT expression
#
# formula : expression COMPARATOR expression
#           | formula BOOLEAN_OPERATOR formula
#           | LPAREN expression RPAREN
#           | VARIABLE
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
#            | NUMBER
#            | VARIABLE

variables = {}

class ParseError(Exception):
    pass

def p_start(p):
    '''start : assignment
             | expression
             | annotation
             | formula
             | declaration'''
    p[0] = p[1]


def p_bool_declaration(p):
    'declaration : BOOL_TYPE VARIABLE'
    if p[2] in variables:
        parser.errorfunc()
    else:
        variables[p[2]] = "BOOL"
        p[0] = Node("bool_declaration",None,p[2],None)

def p_int_declaration(p):
    'declaration : INT_TYPE VARIABLE'
    if p[2] in variables:
        parser.errorfunc()
    else:
        variables[p[2]] = "INT"
        p[0] = Node("int_declaration",None,p[2],None)


def p_annotation(p):
    'annotation : ANNOTATION formula'
    p[0] = Node('annotation',p[1], p[2], None)


def p_assignment(p):
    'assignment : VARIABLE ASSIGNMENT expression'
    p[0] = Node('assignment',  p[2], p[1], p[3])


def p_expression_plus(p):
    'expression : expression PLUS expression'
    p[0] = Node('plus', p[2], p[1], p[3])

def p_expression_minus(p):
    'expression : expression MINUS expression'
    p[0] = Node('minus', p[2], p[1], p[3])

def p_expression_times(p):
    'expression : expression TIMES expression'
    p[0] = Node('times', p[2], p[1], p[3])

def p_parenthesis_expr(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_num(p):
    'expression : NUMBER'
    p[0] = Node('NUMBER',None, p[1], None)

def p_expression_variable(p):
    'expression : VARIABLE'
    if not p[1] in variables or variables[p[1]] != "INT":
        raise ParseError("variable not defined or invalid operation")
    p[0] = Node('variables',None, p[1],None)

def p_expr_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = Node("unary minus",p[1],-p[2],None)


def p_formula_comparison(p):
    'formula : expression COMPARATOR expression'
    p[0] = Node('comparison', p[2], p[1], p[3])

def p_formula_logic_op(p):
    'formula : formula BOOLEAN_OPERATOR formula'
    p[0] = Node('boolean', p[2], p[1], p[3])

def p_formula_variable(p):
    'formula : VARIABLE'
    if not p[1] in variables or variables[p[1]] != "BOOL":
        raise ParseError("variable not defined or invalid operation")
    p[0] = Node('variables',None, p[1], None)

def p_formula_expr(p):
    'formula : LPAREN formula RPAREN'
    p[0] = p[2]



precedence = (
    ('nonassoc', 'COMPARATOR'),
    ('left', 'BOOLEAN_OPERATOR'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES'),
    ('right', 'UMINUS'),
)

# def p_statement_annotation(p):
#     'statement : annotation'
#     p[0] = p[1]
#
# def p_statement_assignment(p):
#     'statement : assignment'
#     p[0] = p[1]
#
# def p_statement_expression(p):
#     'statement : expression'
#     p[0] = p[1]
#
# def p_annotation(p):
#     'annotation : ANNOTATION expression'
#     p[0] = Node('annotation',p[1], p[2], None)
#
# def p_assignment(p):
#     'assignment : VARIABLE ASSIGNMENT expression'
#     p[0] = Node('assignment',  p[2], p[1], p[3])
#
# def p_comparison(p):
#     'expression : expression COMPARATOR term'
#     p[0] = Node('comparison', p[2], p[1], p[3])
#
# def p_logic_op(p):
#     'expression : expression BOOLEAN_OPERATOR term'
#     p[0] = ('boolean', p[2], p[1], p[3])
#
# def p_term_variable(p):
#     'term : VARIABLE'
#     p[0] = Node('variables',None, p[1],None)
#
# def p_expression_plus(p):
#     'expression : expression PLUS expression'
#     p[0] = Node('plus', p[2], p[1], p[3])
#
# def p_expression_minus(p):
#     'expression : expression MINUS term'
#     p[0] = Node('minus', p[2], p[1], p[3])
#
# def p_expression_term(p):
#     'expression : term'
#     p[0] = p[1]
#
# def p_term_times(p):
#     'term : term TIMES factor'
#     p[0] = Node('times', p[2], p[1], p[3])
#
# def p_term_boolean(p):
#     'term : TRUE'
#     p[0] = Node('Boolean', None,p[1],None)
#
# # def p_term_div(p):
# #     'term : term DIVIDE factor'
# #     p[0] = p[1] / p[3]
#
# def p_term_factor(p):
#     'term : factor'
#     p[0] = p[1]
#
# def p_factor_num(p):
#     'factor : NUMBER'
#     p[0] = Node('NUMBER',None, p[1], None)
#
# def p_factor_expr(p):
#     'factor : LPAREN expression RPAREN'
#     p[0] = p[2]

# Error rule for syntax errors
def p_error(p):
    # print("Syntax error in input!")
    raise ParseError("Syntax error in input!")



# Build the parser
parser = yacc.yacc()

def gen_new_symbol(symbol):
    return symbol + ''

def generate_vc():
    with open('code.tms') as f:
        statements = []
        for line in f.readlines():
            statements.append(parser.parse(line))
            # print(parser.parse(line).print_node_rec())
        conditions = []
        body = []
        for statement in statements:
            statement_type = statement.symbol
            if statement_type == "annotation":
                conditions.append(statement)
            elif statement_type == "assignment":
                body.append(statement)
            else:
                # if already parsed and it is not an assignment or annotation
                # then it is a correct statement with no effect
                continue
                # raise Exception("Not covered", statement_type)
        body = body[::-1] # Reverse
        variables = {} # Variable -> statement
        substitutions = {} # Variable -> New Variable
        for statement in body: # Assume body all has assignments
            variable = statement.left
            rhs_expr = statement.right
            new_variable = gen_new_symbol(variable)
            variables[new_variable] = rhs_expr
            # substitute in my post-cond
            conditions[-1] = conditions[-1].subst({variable: rhs_expr})
            # substitutions[variable] = new_variable
        print(conditions[-1].print_node_rec())
        return conditions[-1]

