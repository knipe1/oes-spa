#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 09:17:48 2020

@author: hauke
"""

# standard libs
from enum import Enum, auto

class ASC_PARAMETER(Enum):
    """Interface for the .asc-file parameter."""
    TEMP = auto()
    WL = auto()
    EX_TIME = auto()
    GRAT = auto()