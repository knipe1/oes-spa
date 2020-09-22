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
from custom_types.BasePeak import BasePeak

# Enums
from custom_types.ERROR_CODE import ERROR_CODE as ERR

@dataclass(frozen=True)
class ReferencePeak(BasePeak):
    """
    Describes the properties of a (reference) peak.

    Usage:
        TODO!


    Attributes
    ----------
    minimum: float = 0.0
        The minimum value(height?/area?) the peak needs to be valid.


    Methods
    -------
    """
    minimum: float = 0.0;           # minimum for a valid Peak


    @property
    def isValid(self):
        error = super(ReferencePeak, self).isValid
        if not self.minimum >= 0:
            error = ERR.INVALID_MINIMUM
        return error