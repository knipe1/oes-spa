#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# TODO: docstring

Created on Thu Apr  9 11:17:15 2020

@author: Hauke Wernecke
"""

# standard libs
import unittest

# third-party libs

# local modules/libs
from modules.dataanalysis.Fitting import Fitting

# Enums

class TestFitting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.fitting = Fitting()

    def tearDown(self):
        pass

    def test_retrieve_fittings(self):
        """
        Test the method retrieve_fittings.

        Prototype: specify_batchfile(self):

        Returns
        -------
        None.

        """
        fittings = self.fitting._retrieve_fittings()
        self.assertEqual(len(fittings), 1, "More files in directory")
        self.assertTrue('boron_fitting.yml' in fittings)

if __name__ == '__main__':
    unittest.main()
