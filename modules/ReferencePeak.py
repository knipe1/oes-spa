#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 2020

@author: hauke
"""

# standard libs
from dataclasses import dataclass

# third-party libs

# local modules/libs

@dataclass(frozen=True)
class ReferencePeak:
    """
    Describes the properties of a (reference) peak.

    Usage:
        TODO!


    Attributes
    ----------
    centralWavelength: float
        The wavelength of the peak.
    shiftUp: float
        The upper limit of the peak regarding the integration.
    shiftDown: float
        The lower limit of the peak regarding the integration.
    minimum: float = 0.0
        The minimum value(height?/area?) the peak needs to be valid.


    Methods
    -------
    """
    centralWavelength: float
    shiftUp: float
    shiftDown: float
    minimum: float = 0.0;           # minimum for a valid Peak

    def __validate(self):
        if not self.shiftUp >= self.centralWavelength:
            raise ValueError("Upper limit has to be greater than central wavelength")
        if not self.shiftDown <= self.centralWavelength:
            raise ValueError("Lower limit has to be smaller than central wavelength")

    def __post_init__(self):
        pass
        # self.__validate()