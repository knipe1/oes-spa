#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 12:07:42 2020

@author: hauke
"""

# standard libs
from enum import Enum

class ERROR_FITTING(Enum):
    """Interface for the .asc-file parameter."""
    PEAK = "P"
    REFERENCE = "R"
    FITTING = "F"
    OTHER = "O"