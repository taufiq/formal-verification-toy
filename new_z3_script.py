from z3 import *
import sys
from time import time
import json

timeout = int(sys.argv[1])
x = Int('x')
y = Int('y')
z = Bool('z')
formula =  (And( z,))
solver = Solver()
solver.set('timeout', timeout * 1000)
solver.add(formula)
print(solver.check())