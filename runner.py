#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file implements a routine to run all test one after another.
Therefore, the test modules are imported and added to a test suite.
For further information see also the official python documnetation about unittests.
https://docs.python.org/3/library/unittest.html

Created on Mon Mar 23 13:09:57 2020
"""

__author__ = "Hauke Wernecke"
__copyright__ = "Copyright 2020"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Hauke Wernecke/Peter Knittel"
__email__ = "hauke.wernecke@iaf.fraunhhofer.de, peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"

# third-party imports
from unittest import TestLoader, TestSuite, TextTestRunner

# classes 
import modules.test_BatchAnalysis as t_batch
import modules.test_FileFramework as t_file
import modules.test_universal as t_uni

import ui.test_UIBatch as t_ui_batch
import ui.test_UIMain as t_ui_main


# initialize the test suite
loader = TestLoader()
suite  = TestSuite()


# add tests to the test suite
suite.addTests(loader.loadTestsFromModule(t_batch))
suite.addTests(loader.loadTestsFromModule(t_file))
suite.addTests(loader.loadTestsFromModule(t_uni))

suite.addTests(loader.loadTestsFromModule(t_ui_batch))
suite.addTests(loader.loadTestsFromModule(t_ui_main))

# initialize a runner, pass it your suite and run it
runner =  TextTestRunner(verbosity=3)
runner.run(suite)