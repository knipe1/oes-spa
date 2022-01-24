#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 17:52:17 2020

@author: hauke
"""


# standard libs
import numpy as np
from dataclasses import dataclass

# third-party libs

# local modules/libs
from c_enum.characteristic import CHARACTERISTIC as CHC
from c_enum.export_type import EXPORT_TYPE

# unsafe_hash=True allows to add Integration instance into a set
@dataclass(unsafe_hash=True)
class Integration():
    data: np.ndarray
    peakType: str = CHC.TYPE_PEAK;
    spectrumType: str = EXPORT_TYPE.RAW;

    @property
    def xData(self):
        return self.data[:, 0]

    @property
    def yData(self):
        return self.data[:, 1]
