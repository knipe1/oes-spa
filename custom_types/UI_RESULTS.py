#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:11:16 2020

@author: hauke
"""



# standard libs
from enum import Enum, auto


class UI_RESULTS(Enum):
    tout_PEAK_HEIGHT = auto()
    tout_PEAK_AREA = auto()
    tout_BASELINE = auto()