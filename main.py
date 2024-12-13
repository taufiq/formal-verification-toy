from distutils.command.config import config


from IR import generate_basic_paths
from z3_script_generator import *
import sys
from project_config import set_debug, get_debug
from plot_graph import generate_graph

if len(sys.argv) > 1 and  sys.argv[1] == "DEBUG":
    set_debug(True)

if get_debug():
    generate_basic_paths()
else:
    trees, basic_paths = generate_basic_paths()
    script = generate_z3_script(trees)
    export_z3pyscript("z3_script.py", script)
    run_z3pyscript("z3_script.py", timeout=10800)
    generate_graph(basic_paths)

