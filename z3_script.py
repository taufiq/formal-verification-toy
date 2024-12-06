from z3 import *
import sys
from time import time
import json

timeout = sys.argv[1]
x = Int('x')
y = Int('y')
z = Bool('z')
formula = ForAll([x,y,z],(And  (Implies( z, ( 3 <=  5))),
 (Implies( ( y <=  5), (And( z, ( x >  y))))),
 (Implies( ( y <=  5), (Implies( ( y <  5), (And( (And( z, z)), ( x >  ( y +  1))))))))))
solver = Solver()
solver.set('timeout', int(timeout * 1000))
solver.add(formula)
print(solver.check())
if solver.check() == sat: 
 	 print(solver.model)
