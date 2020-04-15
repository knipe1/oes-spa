#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# TODO: docstring

Created on Thu Apr 15 2020

@author: Hauke Wernecke
"""

# standard libs

# third-party libs

# local modules/libs

# Enums

class Peak():
    # name as a neccessary attribute or overhead for reference peaks?
    _name = "";
    _centralWavelength = 0;
    _upperLimit = 0;        # or use a shift? _posShift
    _lowerLimit = 0;        # _negShift
    # minimum as a neccessary attribute? Even for reference peaks?
    _minimum = 0;           # minimum for a valid Peak
    _reference = [];        # reference peaks

    def __init__(self, centralWavelength, upperLimit, lowerLimit):
        # assign the attributes
        pass

    def addReference(self, Peak):
        # adding a peak as a reference to evaluate the characteristic value
        pass

    def calculate_characteristic_value(self):
        # calculating the value if references are given
        # and checking against the minimum value
        pass