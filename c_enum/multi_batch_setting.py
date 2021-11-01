#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 10:54:20 2021

@author: hauke
"""

# standard libs
from enum import IntEnum
from collections import namedtuple


MultiBatchSetting = namedtuple('Setting', ['peakname', 'characteristic', 'xoffset', 'yoffset'])



class MultiBatchColumns(IntEnum):
    COL_FILENAME = 0
    COL_PEAKNAME = 1
    COL_CHARACTERISTIC = 2
    COL_X_OFFSET = 3
    COL_Y_OFFSET = 4
