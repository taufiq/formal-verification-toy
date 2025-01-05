import os
from logging import exception
from os import walk
from IR import *
from parser import *

SHOULD_PASS = "tests/should_pass"
SHOULD_FAIL = "tests/should_fail"
SHOULD_THROW_ERROR = "tests/should_throw_error"


for (dirpath, dirnames, filenames) in walk(SHOULD_PASS):

    for filename in filenames:
        reset_functions()
        print("")
        print("### running tests for " + filename + " ###")
        print("")
        assert(generate_basic_paths(os.path.join(dirpath, filename)))
        print("")
        print("# Test passed for " + filename + " #")

for (dirpath, dirnames, filenames) in walk(SHOULD_FAIL):
    for filename in filenames:
        reset_functions()
        print("")
        print("### running tests for " + filename + " ###")
        print("")
        assert (not(generate_basic_paths(os.path.join(dirpath, filename))))
        print("# Test passed for " + filename + " #")

for (dirpath, dirnames, filenames) in walk(SHOULD_THROW_ERROR):
    for filename in filenames:
        reset_functions()
        print("")
        print("### running tests for " + filename + " ###")
        print("")
        try:
            generate_basic_paths(os.path.join(dirpath, filename))
        except BaseException as e:
            assert(True)
            print(e)
            print("")
            print("# Test passed for " + filename + " #")
        else:
            assert(False)

