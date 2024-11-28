from lexer import tokens
import ply.yacc as yacc


class Node:
    def __init__(self,symbol,op,left,right):
        self.left = left
        self.right = right
        self.op = op
        self.symbol = symbol

    def print_node_rec(self):
        if (self.left is not None) and (self.right is not None):
            if isinstance(self.left, Node) and isinstance(self.right, Node):
                return "(" + self.symbol + "," + self.left.print_node_rec() + " " + self.right.print_node_rec() + ")"
            elif isinstance(self.left, Node):
                return "(" + self.symbol + "," + self.left.print_node_rec() + " " + str(self.right) + ")"
            elif isinstance(self.right, Node):
                return "(" + self.symbol + "," + str(self.left) + " " + self.right.print_node_rec() + ")"
            else:
                return "(" + self.symbol + "," + str(self.left)  + " " + str(self.right) + ")"
        elif self.left is not None:
            if isinstance(self.left, Node):
                return "(" + self.symbol + "," + self.left.print_node_rec() + ")"
            else:
                return "(" + self.symbol + "," + str(self.left) + ")"

    def subst(self, mapping):
        if self is None:
            return
        if isinstance(self, Node):
            if self.symbol == "variables" and self.left in mapping:
                return mapping[self.left]
            else:
                if isinstance(self.left, Node) and isinstance(self.right, Node):
                    return Node(self.symbol, self.op, self.left.subst(mapping), self.right.subst(mapping))
                elif isinstance(self.left, Node):
                    return Node(self.symbol, self.op, self.left.subst(mapping), self.right)
                elif isinstance(self.right, Node):
                    return Node(self.symbol, self.op, self.left, self.right.subst(mapping))
                else:
                    return Node(self.symbol, self.op, self.left, self.right)






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
    p[0] = Node('annotation',p[1], p[2], None)

def p_assignment(p):
    'assignment : VARIABLE ASSIGNMENT expression'
    p[0] = Node('assignment',  p[2], p[1], p[3])

def p_comparison(p):
    'expression : expression COMPARATOR term'
    p[0] = Node('comparison', p[2], p[1], p[3])

def p_logic_op(p):
    'expression : expression BOOLEAN_OPERATOR term'
    p[0] = ('boolean', p[2], p[1], p[3])

def p_term_variable(p):
    'term : VARIABLE'
    p[0] = Node('variables',None, p[1],None)

def p_expression_plus(p):
    'expression : expression PLUS expression'
    p[0] = Node('plus', p[2], p[1], p[3])

def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = Node('minus', p[2], p[1], p[3])

def p_expression_term(p):
    'expression : term'
    p[0] = p[1]

def p_term_times(p):
    'term : term TIMES factor'
    p[0] = Node('times', p[2], p[1], p[3])

def p_term_boolean(p):
    'term : TRUE'
    p[0] = Node('Boolean', None,p[1],None)

# def p_term_div(p):
#     'term : term DIVIDE factor'
#     p[0] = p[1] / p[3]

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_factor_num(p):
    'factor : NUMBER'
    p[0] = Node('NUMBER',None, p[1], None)

def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")



# Build the parser
parser = yacc.yacc()

def gen_new_symbol(symbol):
    return symbol + ''

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

