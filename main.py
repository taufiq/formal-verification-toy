from z3_script_generator import *

tree = generate_vc()
script = generate_z3_script(tree)
export_z3pyscript("z3_script.py", script)
run_z3pyscript("new_z3_script.py", timeout=10800)
