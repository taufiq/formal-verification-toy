import ply.lex as lex

reserved = {
   'TRUE' : 'TRUE',
   'FALSE' : 'FALSE',
   "INT" : "INT_TYPE",
   "BOOL" : "BOOL_TYPE",
   'IF': 'IF',
   'THEN': 'THEN',
   'ELSE': 'ELSE',
}
# List of token names.   This is always required
tokens = [
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   # 'DIVIDE',
   'LPAREN',
   'RPAREN',
   'ANNOTATION',
   'VARIABLE',
   'COMPARATOR',
   'BOOLEAN_OPERATOR',
#    'LESSER_THAN',
#    'LESSER_THAN_EQUAL',
#    'GREATER_THAN',
#    'GREATER_THAN_EQUAL',
   'ASSIGNMENT',
   'TRUTH_VALUES',
   # 'INT_TYPE',
   # 'BOOL_TYPE',
   'ASSUME',
   'IMPLIES',
] + list(reserved.values())

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
# t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
# t_BOOL_TYPE = r'\bBOOL\b'
# t_INT_TYPE = r'\bINT\b'
# t_BOOLEAN = r'(TRUE|FALSE)'
# t_LESSER_THAN = r'<'
# t_LESSER_THAN_EQUAL = r'<='
# t_GREATER_THAN = r'>'
# t_GREATER_THAN_EQUAL = r'>='
t_ASSIGNMENT = r':='
t_IMPLIES = r'=>'



def t_TRUTH_VALUES(t):
    r'(TRUE|FALSE)'
    t.type = reserved.get(t.value,'TRUTH_VALUES')
    return t

def t_ASSUME(t):
    r'assume'
    return t

def t_COMPARATOR(t):
    r'(>=|<=|<|>)'
    return t

def t_BOOLEAN_OPERATOR(t):
    r'(\^|v)'
    return t

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_ANNOTATION(t):
    r'\@'
    return t

def t_VARIABLE(t):
    r'\w+'
    t.type = reserved.get(t.value, 'VARIABLE')
    return t


# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# LexToken(self.type, self.value, self.lineno, self.lexpos)
# data = '''
# INT x
# '''
#
# # Give the lexer some input
# lexer.input(data)
#
# # Tokenize
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(tok)