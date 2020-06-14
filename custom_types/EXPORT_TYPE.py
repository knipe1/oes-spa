#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 10:13:32 2020

@author: hauke
"""


# standard libs
from enum import Enum, auto


class EXPORT_TYPE(Enum):
    """Provide an interace for file properties depending on the export type."""
    RAW = auto()
    PROCESSED = auto()
    BATCH = auto()