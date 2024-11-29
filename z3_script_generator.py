from Node import Node
import z3_config

def imports():
    imports = f'from z3 import *\n' \
              f'import sys\n' \
              f'from time import time\n' \
              f'import json\n' \
              f'\n'
    return imports


def generate_variables(tree:Node):
    if tree.symbol == "variables":



def main(tree:Node):
    generate_variables(tree)
