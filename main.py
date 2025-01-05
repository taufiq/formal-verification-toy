from IR import generate_basic_paths
import sys
# and  sys.argv[1] == "DEBUG":


class InputError(Exception):
    def __init__(self, message="program takes only the file path as input"):
        super().__init__(message)

class UnsupportedFileExtension(Exception):
    def __init__(self, message="Only .tpl files are supported."):
        super().__init__(message)

if len(sys.argv) < 2:
    raise InputError(message="Usage: python main.py <file>")

if len(sys.argv) > 2 :
    raise InputError()

if sys.argv[1].split("/")[-1].split(".")[-1] != "tpl" :
    raise UnsupportedFileExtension()


generate_basic_paths(sys.argv[1])
    # script = generate_z3_script(trees)
    # export_z3pyscript("z3_script.py", script)
    # run_z3pyscript("z3_script.py", timeout=30)
    # generate_graph(basic_paths)

