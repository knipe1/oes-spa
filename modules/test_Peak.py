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
import threading as thrd

# local modules/libs
from modules.Peak import Peak
from modules.ReferencePeak import ReferencePeak

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

    def test_valid_init_ReferencePeak(self):
        # def values
        cWl = 334.5
        upperLimit = 450
        lowerLimit = 200
        minimum = 0.2
        # first init with def. minimum
        refPeak = ReferencePeak(cWl, upperLimit, lowerLimit)
        self.assertTrue(isinstance(refPeak, ReferencePeak))
        # sec init with explicit minimum
        refPeak = ReferencePeak(cWl, upperLimit, lowerLimit, minimum)
        self.assertTrue(isinstance(refPeak, ReferencePeak))
        # ensure correct assignment
        self.assertEqual(refPeak.centralWavelength, cWl)
        self.assertEqual(refPeak.upperLimit, upperLimit)
        self.assertEqual(refPeak.lowerLimit, lowerLimit)
        self.assertEqual(refPeak.minimum, minimum)

    def test_invalid_init_ReferencePeak(self):
        # def values
        cWl = 334.5
        upperLimit = 450
        lowerLimit = 200
        InvalidUpperLimit = 2
        InvalidLowerLimit = 500

        with self.assertRaises(ValueError):
            ReferencePeak(cWl, upperLimit, lowerLimit)
            ReferencePeak(cWl, InvalidUpperLimit, lowerLimit)
            ReferencePeak(cWl, upperLimit, InvalidLowerLimit)
            ReferencePeak(cWl, InvalidUpperLimit, InvalidLowerLimit)

    def test_valid_init_Peak(self):
        # def values
        name = "CN-Value"
        cWl = 334.5
        upperLimit = 450
        lowerLimit = 200
        # first init with def. name
        peak = Peak(cWl, upperLimit, lowerLimit)
        self.assertIsInstance(peak, Peak)
        self.assertIsInstance(peak, Peak)

        # second init with explicit name
        peak = Peak(cWl, upperLimit, lowerLimit, name = name)
        # ensure correct assignment
        self.assertEqual(peak.centralWavelength, cWl)
        self.assertEqual(peak.upperLimit, upperLimit)
        self.assertEqual(peak.lowerLimit, lowerLimit)
        self.assertEqual(peak.name, name)



    def test_addReference(self):
        # def values
        name = "CN-Value"
        cWl = 334.5
        upperLimit = 450
        lowerLimit = 200
        # init
        refPeak = ReferencePeak(cWl, upperLimit, lowerLimit)
        peak = Peak(cWl, upperLimit, lowerLimit, name = name)

        peak.addReference(refPeak)      # added
        peak.addReference(upperLimit)   # not added

        for ref in peak.reference:
            self.assertIsInstance(ref, ReferencePeak)



if __name__ == '__main__':
    unittest.main()
