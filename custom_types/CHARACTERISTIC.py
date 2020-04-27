#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 13:28:14 2020

@author: hauke
"""


# standard libs
from enum import Enum

class CHARACTERISTIC(Enum):
    """Including the labels to link numerical values to characteristic ones."""
    PEAK_HEIGHT = "Peak height"
    PEAK_AREA = "Peak area"
    BASELINE = "Baseline"
    PEAK_POSITION = "Peak position"
    HEADER_INFO = "Header info"

