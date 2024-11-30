from z3 import *
import sys
from time import time
import json

timeout = int(sys.argv[1])
x = Int('x')
z = Bool('z')
formula =  (And( z, ( ( x +  1) >  3)))
solver = Solver()
print("----> Timeout: ", timeout)
solver.set('timeout', timeout * 1000)
solver.add(formula)
print(solver.check())