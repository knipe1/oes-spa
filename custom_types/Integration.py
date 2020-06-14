#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 17:52:17 2020

@author: hauke
"""


# standard libs
from dataclasses import dataclass

# third-party libs

# local modules/libs
from custom_types.EXPORT_TYPE import EXPORT_TYPE
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC

# unsafe_hash=True allows to add Integration instance into a set
@dataclass(unsafe_hash=True)
class Integration():
    xData: list;
    yData: list;
    peakType: str = CHC.TYPE_PEAK;
    spectrumType: str = EXPORT_TYPE.RAW;