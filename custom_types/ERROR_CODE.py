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
    UNKNOWN_FILETYPE = auto()
    INVALID_DATA = auto()
    DATA_UNEQUAL_LENGTH = auto()
    INVALID_FILEINFORMATION = auto()
    INVALID_HEADER = auto()