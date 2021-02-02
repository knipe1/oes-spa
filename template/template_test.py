#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# TODO: docstring

Created on Thu Apr 16 10:53:38 2020

"""

# standard libs
import unittest

# third-party libs
import emulator as emu
import threading as THR

# local modules/libs
from loader.ConfigLoader import ConfigLoader
# HINT: import module here

# Enums

class TestModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_method(self):
        pass


if __name__ == '__main__':
    unittest.main()

# How to Use Contextmanager:
# with AssertRaises(ValueError):
#     calc.divide(20,-2)
#     calc.divide(10,0)
