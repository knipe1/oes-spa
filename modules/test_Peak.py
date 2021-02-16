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
from c_types.peak import Peak
from c_types.referencepeak import ReferencePeak

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
        shiftUp = .2
        shiftDown = .2
        minimum = 0.2
        # first init with def. minimum
        refPeak = ReferencePeak(cWl, shiftUp, shiftDown)
        self.assertTrue(isinstance(refPeak, ReferencePeak))
        # sec init with explicit minimum
        refPeak = ReferencePeak(cWl, shiftUp, shiftDown, minimum)
        self.assertTrue(isinstance(refPeak, ReferencePeak))
        # ensure correct assignment
        self.assertEqual(refPeak.centralWavelength, cWl)
        self.assertEqual(refPeak.shiftUp, shiftUp)
        self.assertEqual(refPeak.shiftDown, shiftDown)
        self.assertEqual(refPeak.minimum, minimum)

    def test_invalid_init_ReferencePeak(self):
        # def values
        cWl = 334.5
        shiftUp = .2
        shiftDown = .2
        InvalidUpperLimit = 2
        InvalidLowerLimit = 500

        with self.assertRaises(ValueError):
            ReferencePeak(cWl, shiftUp, shiftDown)
            ReferencePeak(cWl, InvalidUpperLimit, shiftDown)
            ReferencePeak(cWl, shiftUp, InvalidLowerLimit)
            ReferencePeak(cWl, InvalidUpperLimit, InvalidLowerLimit)

    def test_valid_init_Peak(self):
        # def values
        name = "CN-Value"
        cWl = 334.5
        shiftUp = .2
        shiftDown = .2
        # first init with def. name
        peak = Peak(cWl, shiftUp, shiftDown)
        self.assertIsInstance(peak, Peak)
        self.assertIsInstance(peak, Peak)

        # second init with explicit name
        peak = Peak(cWl, shiftUp, shiftDown, name = name)
        # ensure correct assignment
        self.assertEqual(peak.centralWavelength, cWl)
        self.assertEqual(peak.shiftUp, shiftUp)
        self.assertEqual(peak.shiftDown, shiftDown)
        self.assertEqual(peak.name, name)



    def test_addReference(self):
        # def values
        name = "CN-Value"
        cWl = 334.5
        shiftUp = .2
        shiftDown = .2
        # init
        refPeak = ReferencePeak(cWl, shiftUp, shiftDown)
        peak = Peak(cWl, shiftUp, shiftDown, name = name)

        peak.addReference(refPeak)      # added
        peak.addReference(shiftUp)   # not added

        for ref in peak.reference:
            self.assertIsInstance(ref, ReferencePeak)



if __name__ == '__main__':
    unittest.main()
