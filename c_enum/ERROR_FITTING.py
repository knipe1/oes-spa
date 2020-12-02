#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 12:07:42 2020

@author: hauke
"""

# standard libs
from enum import Enum, unique

@unique
class ERROR_FITTING(Enum):
    OK = ""
    PEAK = "P"
    REFERENCE = "R"
    FITTING = "F"
    OTHER = "O"