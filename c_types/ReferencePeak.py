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
from c_types.BasePeak import BasePeak

# Enums
from c_enum.ERROR_CODE import ERROR_CODE as ERR

@dataclass(frozen=True)
class ReferencePeak(BasePeak):
    """
    Describes the properties of a (reference) peak.


    Attributes
    ----------
    minimumHeight: float = 0.0
        The minimum value the peak needs to be valid.
    """
    minimumHeight: float = 0.0


    @property
    def isValid(self):
        error = super().isValid
        if not self.minimumHeight >= 0:
            error = ERR.INVALID_MINIMUM
        return error