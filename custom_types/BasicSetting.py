#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 20:27:58 2020

@author: hauke
"""


# standard libs
from dataclasses import dataclass

# third-party libs

# local modules/libs
from modules.Fitting import Fitting

@dataclass(frozen=True)
class BasicSetting():
    wavelength: float;
    grating: float; # TODO: int?
    fitting: Fitting;