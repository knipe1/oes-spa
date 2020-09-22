#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 11:44:18 2020

@author: Hauke Wernecke
"""

# standard libs
from dataclasses import dataclass

# third-party libs

# local modules/libs

# Enums
from custom_types.ERROR_CODE import ERROR_CODE as ERR

@dataclass(frozen=True)
class BasePeak():
    """
    Basic interface for (reference) peaks.


    Attributes
    ----------
    centralWavelength: float
        The wavelength of the peak.
    shiftUp: float
        The upper limit of the peak regarding the integration.
    shiftDown: float
        The lower limit of the peak regarding the integration.
    isValid: ERROR_CODE
        ERR.OK if is valid

    """
    centralWavelength: float
    shiftUp: float
    shiftDown: float


    @property
    def isValid(self):
        error = ERR.OK
        if not self.centralWavelength >= 0:
            error = ERR.INVALID_WAVELENGTH
        elif not self.shiftUp >= 0:
            error = ERR.INVALID_LIMIT
        elif not self.shiftDown >= 0:
            error = ERR.INVALID_LIMIT
        return error

