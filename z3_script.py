from z3 import *
import sys
from time import time
import json

timeout = 100
x = Int('x')
z = Bool('z')
formula =  (And( z, ( ( x +  1) >  3)))
solver = Solver()
solver.set('timeout', int(timeout * 1000))
solver.add(formula)
print(solver.check())