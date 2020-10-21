#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 15:23:11 2020

@author: hauke
"""


# standard libs
from enum import Enum, auto


class ERROR_CODE(Enum):
    """Provide an interace for file properties depending on the export type."""
    OK = 0
    UNKNOWN_ERROR = auto()
    UNKNOWN_FILETYPE = auto()
    INVALID_DATA = auto()
    INVALID_BATCHFILE = auto()
    DATA_UNEQUAL_LENGTH = auto()
    INVALID_FILEINFORMATION = auto()
    INVALID_HEADER = auto()
    INVALID_WAVELENGTH = auto()
    INVALID_LIMIT = auto()
    INVALID_MINIMUM = auto()
    INVALID_NORM_FACTOR = auto()

    def __bool__(self):
        return (self == self.OK)
