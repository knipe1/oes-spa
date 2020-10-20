#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 09:48:04 2020

@author: hauke
"""


# standard libs

# third-party libs

# local modules/libs
from custom_types.BasePeak import BasePeak
from custom_types.ReferencePeak import ReferencePeak
from dialog_messages import information_normalizationFactorUndefined

# Enums
from custom_types.ERROR_CODE import ERROR_CODE as ERR

# constants
DEFAULT_NORM_FACTOR = 1.0
DEFAULT_NORM_OFFSET = 0.0

def default_norm_factor():
    """Prompt the user and set the default."""
    information_normalizationFactorUndefined()
    return DEFAULT_NORM_FACTOR

class Peak(BasePeak):

    def __init__(self, name:str, centralWavelength:float, shiftUp:float, shiftDown:float, normalizationFactor:float=None, normalizationOffset:float=None, **kwargs):

        super().__init__(centralWavelength, shiftUp, shiftDown)
        self.name = name

        if normalizationFactor is None:
            normalizationFactor = default_norm_factor()
        self.normalizationFactor = normalizationFactor

        self.normalizationOffset = normalizationOffset or DEFAULT_NORM_OFFSET

        ref = kwargs.get("reference")
        self.set_reference(ref)


    def set_reference(self, ref):
        """
        Undefined: Omitting attribute
        Unproperly defined: reference = None
        Properly defined: reference is a ReferencePeak
        """

        if ref:
            try:
                self.reference = ReferencePeak(**ref)
            except TypeError:
                self.reference = None


    @property
    def isValid(self):
        error = super().isValid
        if not self.normalizationFactor >= 0:
            error = ERR.INVALID_NORM_FACTOR
        return error

