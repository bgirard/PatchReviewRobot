#!/usr/bin/python
#
# Any copyright is dedicated to the Public Domain.
# http://creativecommons.org/publicdomain/zero/1.0/
#

import filecmp
import tempfile
import checkmozstyle
import subprocess
import os
import sys
import modules.cpplint as cpplint

#filecmp.cmp('undoc.rst', 'undoc.rst') 
#tempFileTuple = tempfile.mkstemp()
#os.write(tempFileTuple[0], "foo\n")

TESTS = [
    # Empty patch
    {
      "patch" : "tests/test1.patch",
      "cpp" : "tests/test1.cpp",
      "out" : "tests/test1.out"
    },
    # Bad header
    {
      "patch" : "tests/test2.patch",
      "cpp" : "tests/test2.cpp",
      "out" : "tests/test2.out"
    },
    # Bad Description
    {
      "patch" : "tests/test3.patch",
      "cpp" : "tests/test3.cpp",
      "out" : "tests/test3.out"
    },
    # readability tests
    {
      "patch" : "tests/test4.patch",
      "cpp" : "tests/test4.cpp",
      "out" : "tests/test4.out"
    },
    # runtime tests
    {
      "patch" : "tests/test5.patch",
      "cpp" : "tests/test5.cpp",
      "out" : "tests/test5.out"
    },
]

def main():

  has_failed = False
  cwd = os.path.abspath('.')
  cpplint.use_mozilla_styles()
  (args, flags) = cpplint.parse_arguments([])

  for test in TESTS:
    patch = open(test["patch"]).read()

    cpplint.prepare_results_to_string()
    checkmozstyle.process_patch(patch, cwd)
    result = cpplint.get_results()

    expected_output = open(test["out"]).read()

    test_status = "PASSED"
    if result != expected_output:
      test_status = "FAILED"
      print "TEST " + test["patch"] + " " + test_status
      print "Got result:\n" + result + "Expected:\n" + expected_output
      has_failed = True
    else: 
      print "TEST " + test["patch"] + " " + test_status


if __name__ == "__main__":
    main()

