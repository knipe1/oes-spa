#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file implements a routine to run all test one after another.

Therefore, the test modules are imported and added to a test suite.
For further information see also the official python documnetation about
unittests.
https://docs.python.org/3/library/unittest.html

Created on Mon Mar 23 13:09:57 2020
"""

# third-party libs
from unittest import TestLoader, TestSuite, TextTestRunner

# local modules/libs
## modules
import modules.test_BatchAnalysis as t_batch
import modules.test_FileFramework as t_file
import modules.test_universal as t_uni
## ui
import ui.test_UIbatch as t_ui_batch
import ui.test_UImain as t_ui_main


# initialize the test suite
loader = TestLoader()  # exactly, it can load additional tests
suite  = TestSuite()   # the environment to run tests


# add tests to the test suite
# modules
suite.addTests(loader.loadTestsFromModule(t_batch))
suite.addTests(loader.loadTestsFromModule(t_file))
suite.addTests(loader.loadTestsFromModule(t_uni))
# ui
suite.addTests(loader.loadTestsFromModule(t_ui_batch))
suite.addTests(loader.loadTestsFromModule(t_ui_main))

# initialize a runner, pass it your suite and run it
runner =  TextTestRunner(verbosity=3)
runner.run(suite)
