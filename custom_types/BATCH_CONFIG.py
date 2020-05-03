#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 13:30:47 2020

@author: hauke
"""


# standard libs
from enum import Enum

class BATCH_CONFIG(Enum):
    """Including the keys for the dictionary of the batch configuration."""
    CHECKBOX = "checkbox"
    VALUE = "value"
    STATUS = "status"
    LABEL = "label"
    NAME = "name"