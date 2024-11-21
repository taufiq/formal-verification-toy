from lexer import tokens
import ply.yacc as yacc

def p_statement_annotation(p):
    'statement : annotation'
    p[0] = p[1]

def p_statement_assignment(p):
    'statement : assignment'
    p[0] = p[1]

def p_statement_expression(p):
    'statement : expression'
    p[0] = p[1]

def p_annotation(p):
    'annotation : ANNOTATION expression'
    p[0] = ('annotation', p[2])

def p_assignment(p):
    'assignment : VARIABLE ASSIGNMENT expression'
    p[0] = ('assignment', p[1], p[2], p[3])

def p_comparison(p):
    'expression : expression COMPARATOR term'
    p[0] = ('comparison', p[1], p[2], p[3])

def p_logic_op(p):
    'expression : expression BOOLEAN_OPERATOR term'
    p[0] = ('boolean', p[1], p[2], p[3])

def p_term_variable(p):
    'term : VARIABLE'
    p[0] = ('variables', p[1])

def p_expression_plus(p):
    'expression : expression PLUS expression'
    p[0] = ('plus', p[1], p[3])

def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = p[1] - p[3]

def p_expression_term(p):
    'expression : term'
    p[0] = p[1]

def p_term_times(p):
    'term : term TIMES factor'
    p[0] = p[1] * p[3]

def p_term_boolean(p):
    'term : TRUE'
    p[0] = ('Boolean', p[1])

def p_term_div(p):
    'term : term DIVIDE factor'
    p[0] = p[1] / p[3]

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_factor_num(p):
    'factor : NUMBER'
    p[0] = ('NUMBER', p[1])

def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

# while True:
#    try:
#        s = input('calc > ')
#    except EOFError:
#        break
#    if not s: continue
#    result = parser.parse(s)
#    print(result)

def gen_new_symbol(symbol):
    return symbol + ''

with open('code.tms') as f:
    statements = []
    for line in f.readlines():
        statements.append(parser.parse(line))
    conditions = []
    body = []
    for statement in statements:
        statement_type = statement[0]
        if statement_type == "annotation":
            conditions.append(statement)
        elif statement_type == "assignment":
            body.append(statement)
        else:
            raise Exception("Not covered", statement_type)
    body = body[::-1] # Reverse
    variables = {} # Variable -> statement
    substitutions = {} # Variable -> New Variable
    for statement in body: # Assume body all has assignments
        variable = statement[0]
        rhs_expr = statement[3]
        new_variable = gen_new_symbol(variable)
        variables[new_variable] = rhs_expr
        # substitute in my post-cond
        substitutions[variable] = new_variable
        pass


def subst(tree, mapping):
    if tree is None:
        return
    if isinstance(tree, list):
        for node in tree:
            if node[0] == "variables":
                node[1] = mapping[node[1]]
            else:
                subst(node, tree)
