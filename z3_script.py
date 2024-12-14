from z3 import *
import sys
from time import time
import json

timeout = sys.argv[1]
x = Int('x')
y = Int('y')
z = Bool('z')
formula = And( (Implies(True, ( 6 <=  6))),
 (Implies( ( y <=  6), (Implies( ( y <  7), (Implies( ( x <=  1), ( 3 <=  2))))))),
 (Implies( ( x <=  2), (Implies( ( x <  2), ( x <=  2))))),
 (Implies( ( x <=  2), (Implies( ( x >=  2), ( y <=  6))))),
 (Implies( ( y <=  6), (Implies( ( y <  7), (Implies( ( x >  1), ( 2 <=  2))))))),
 (Implies( ( x <=  2), (Implies( ( x <  2), ( x <=  2))))),
 (Implies( ( x <=  2), (Implies( ( x >=  2), ( y <=  6))))),
 (Implies( ( y <=  6), (Implies( ( y >=  7), ( y <  8))))))
formula_for_all = ForAll([x,y,z], formula)
solver = Solver()
solver.set('timeout', int(timeout * 1000))
solver.add(formula_for_all)
print(solver.check())
if solver.check() == unsat:
    solver = Solver()
    solver.add(Not(formula))
    solver.check()
    print('counter example:')
    print(solver.model())
