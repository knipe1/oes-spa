#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 20:27:58 2020

@author: Hauke Wernecke
"""


# standard libs
from dataclasses import dataclass

# third-party libs

# local modules/libs
from modules.dataanalysis.Fitting import Fitting

@dataclass(frozen=True)
class BasicSetting():
    wavelength: float;
    selectedFitting: Fitting;
    checkedFittings:list;
    baselineCorrection: bool;
    normalizeData: bool;