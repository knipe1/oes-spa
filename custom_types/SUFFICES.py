#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 18:58:30 2020

@author: Hauke Wernecke
"""


# standard libs
from enum import Enum

class SUFFICES(Enum):
    """Includes the valid suffices."""
    ASC = "asc"
    CSV = "csv"
    SPK = "spk"
    BATCH = "ba"

    @classmethod
    def has_value(cls, value):
        # The member called _value2member_map_(which is undocumented and may be changed/removed in future python versions).
        return value in cls._value2member_map_

    @classmethod
    def value_set(cls):
        return set(item.value for item in cls)