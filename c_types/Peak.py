#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 09:48:04 2020

@author: hauke
"""


# standard libs

# third-party libs

# local modules/libs
from c_types.BasePeak import BasePeak
from c_types.ReferencePeak import ReferencePeak
from dialog_messages import information_normalizationFactorUndefined, information_normalizationOffsetUndefined

# Enums
from c_enum.error_code import ERROR_CODE as ERR

# constants
DEFAULT_NORM_FACTOR = 1.0
DEFAULT_NORM_OFFSET = 0.0


class Peak(BasePeak):

    def __init__(self, name:str, centralWavelength:float, shiftUp:float, shiftDown:float, normalizationFactor:float=None, normalizationOffset:float=None, **kwargs):

        super().__init__(centralWavelength, shiftUp, shiftDown)
        if name is None:
            raise ValueError ("Name cannot be None.")
        self.name = name

        self.set_normFactor(normalizationFactor)
        self.set_normOffset(normalizationOffset)

        ref = kwargs.get("reference")
        self.set_reference(ref)


    def set_reference(self, ref:dict)->None:
        """
        Undefined: reference = None
        Unproperly defined: Omitting attribute
        Properly defined: reference is a ReferencePeak
        """

        if ref:
            try:
                self.reference = ReferencePeak(**ref)
            except TypeError:
                pass
        else:
            self.reference = None


    def has_valid_reference(self)->None:
        if not hasattr(self, "reference"):
            raise ValueError("Reference peak is not properly defined!")
        elif self.reference is None:
            return self.reference
        else:
            return self.reference.isValid


    @property
    def isValid(self)->bool:
        error = super().isValid
        if not self.is_valid_normalizationFactor():
            error = ERR.INVALID_NORM_FACTOR
        if not self.is_valid_normalizationOffset():
            error = ERR.INVALID_NORM_OFFSET
        return error


    def set_normFactor(self, normFactor:float):
        try:
            float(normFactor)
        except (ValueError, TypeError):
            normFactor = self.default_norm_factor()

        self.normalizationFactor = normFactor


    def set_normOffset(self, normOffset:float):
        try:
            float(normOffset)
        except (ValueError, TypeError):
            normOffset = self.default_norm_offset()

        self.normalizationOffset = normOffset


    def default_norm_factor(self):
        """Prompt the user and set the default."""
        information_normalizationFactorUndefined()
        return DEFAULT_NORM_FACTOR


    def default_norm_offset(self):
        """Prompt the user and set the default."""
        information_normalizationOffsetUndefined()
        return DEFAULT_NORM_OFFSET


    def is_valid_normalizationOffset(self):
        try:
            float(self.normalizationOffset)
            return True
        except ValueError:
            return False


    def is_valid_normalizationFactor(self):
        try:
            if self.normalizationFactor >= 0:
                return True
        except ValueError:
            pass
        return False
