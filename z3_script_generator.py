from Node import Node
from parser import variables
from project_config import Z3INT, Z3BOOL

import subprocess
from subprocess import PIPE


class Z3GenerateFormulaError(Exception):
    def __init__(self, message="invalid formula."):
        super().__init__(message)


def generate_imports():
    imports = f'from z3 import *\n' \
              f'import sys\n' \
              f'from time import time\n' \
              f'import json\n' \
              f'\n'
    return imports

def generate_arguments():
    arguments = "timeout = sys.argv[1]\n"
    return arguments

def generate_variables():
    var_declarations = ""
    for var in variables:
        if variables[var] == 'INT':
            var_declarations += f"{var} = {Z3INT}('{var}')\n"
        else:
            var_declarations += f"{var} = {Z3BOOL}('{var}')\n"
    return var_declarations

def generate_solver():
    solver = "solver = Solver()\n"
    solver += f"solver.set('timeout', int(timeout * 1000))\n"
    solver += f"solver.add(formula_for_all)\n"

    solver += f"print(solver.check())\n\
if solver.check() == unsat:\n\
    solver = Solver()\n\
    solver.add(Not(formula))\n\
    solver.check()\n\
    print('counter example:')\n\
    print(solver.model())\n"
    return solver

def generate_formula(tree:Node):
    formula = ""
    if tree.symbol == "annotation":
        formula += f"{generate_formula(tree.left)}"
    elif tree.symbol == "plus":
        formula += f" ({generate_formula(tree.left)} + {generate_formula(tree.right)})"
    elif tree.symbol == "minus":
        formula += f" ({generate_formula(tree.left)} - {generate_formula(tree.right)})"
    elif tree.symbol == "times":
        formula += f" ({generate_formula(tree.left)} * {generate_formula(tree.right)})"
    elif tree.symbol == "NUMBER":
        formula += f" {tree.left}"
    elif tree.symbol == "variables":
        formula += f" {tree.left}"
    elif tree.symbol == "unary minus":
        formula += f" (-{generate_formula(tree.left)})"
    elif tree.symbol == "comparison":
        formula += f" ({generate_formula(tree.left)} {tree.op} {generate_formula(tree.right)})"
    elif tree.symbol == "boolean" and tree.op == "^":
        formula += f" (And({generate_formula(tree.left)},{generate_formula(tree.right)}))"
    elif tree.symbol == "boolean" and tree.op == "v":
        formula += f" (Or({generate_formula(tree.left)},{generate_formula(tree.right)}))"
    elif tree.symbol == "implies" and tree.op == "=>":
        formula += f" (Implies({generate_formula(tree.left)},{generate_formula(tree.right)}))"
    elif tree.symbol == 'if_then_else':
        condition, then_body, else_body = tree.left
        formula += f"If({generate_formula(condition)}, {generate_formula(then_body)}, {generate_formula(else_body)})"
    elif tree.symbol == "BOOLEAN":
        if tree.left == "TRUE":
            formula += f"True"
        elif tree.left == "FALSE":
            formula += f"False"
    else:
        raise Z3GenerateFormulaError()
    return formula

def generate_formulas(trees):
    formulas = []
    for tree in trees:
        formulas.append(generate_formula(tree))
    formulas = ",\n".join(formulas)
    formulas =  f'formula = And({formulas})\n'
    formulas += f'formula_for_all = ForAll([{",".join(variables)}], formula)\n'
    return formulas

def run_z3pyscript(output_path, timeout=10800):
    process = subprocess.run(["python3", output_path, f'{timeout}'], stderr=PIPE, stdout=PIPE)
    if process.stderr:
        print(f"{process.stderr.decode()}")
        raise Exception(f'Cannot run file {output_path}')
    print(process.stdout.decode())

def export_z3pyscript(out_path, script):
    with open(out_path, 'w') as z:
        z.writelines(script)

def generate_z3_script(trees):
    script = ""
    script += generate_imports()
    script += generate_arguments()
    script += generate_variables()
    script += generate_formulas(trees)
    script += generate_solver()
    return script




