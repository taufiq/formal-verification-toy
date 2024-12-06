
Z3BOOL = 'Bool'
Z3XOR = 'Xor'
Z3INT = 'Int'

DEBUG = False

def set_debug(value: bool):
    global DEBUG
    DEBUG = value


def get_debug():
    return DEBUG