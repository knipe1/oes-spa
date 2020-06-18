#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 09:48:04 2020

@author: hauke
"""


# standard libs
from dataclasses import dataclass, field
from typing import List

# third-party libs

# local modules/libs
from custom_types.ReferencePeak import ReferencePeak
from dialog_messages import information_NormalizationFactor


def set_factor():
    """If no value provided, prompt the user and set the default."""
    default = 1.0
    information_NormalizationFactor()
    return default

@dataclass(frozen=True)
class Peak(ReferencePeak):
    name: str = "";
    normalizationFactor: float = field(default_factory=set_factor);
    reference: List[ReferencePeak] = field(default_factory=list);

    def add_reference(self, reference: ReferencePeak):
        if isinstance(reference, ReferencePeak):
            self.reference.append(reference)

    def __post_init__(self):
        self.__validate__()

    def __validate__(self):
        if not self.normalizationFactor >= 0:
            self.isValid = False

