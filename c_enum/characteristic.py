#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 13:28:14 2020

@author: hauke
"""


# standard libs
from enum import Enum, auto

class CHARACTERISTIC(Enum):
    """Including the labels to link numerical values to characteristic ones."""
    FILENAME = "Filename"
    PEAK_HEIGHT = "Peak height"
    PEAK_AREA = "Peak area"
    BASELINE = "Baseline"
    PEAK_POSITION = "Peak position"
    REF_HEIGHT = "Reference height"
    REF_AREA = "Reference area"
    REF_POSITION = "Reference position"
    HEADER_INFO = "Header info"
    CHARACTERISTIC_VALUE = "Characteristic value"
    PEAK_NAME = "Peak name"
    CALIBRATION_SHIFT = "Calibration shift"
    CALIBRATION_PEAKS = "Calibration peaks"
    FITTING_FILE = "Filename of Fitting"
    INTEGRATION_RAW = auto()
    INTEGRATION_PROCESSED = auto()
    TYPE_PEAK = auto()
    TYPE_REFERENCE = auto()
