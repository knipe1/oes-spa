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

@dataclass(frozen=True)
class Peak(ReferencePeak):
    name: str = "";
    normalizationFactor: float = 1.0;
    reference: List[ReferencePeak] = field(default_factory=list);

    def add_reference(self, reference: ReferencePeak):
        if isinstance(reference, ReferencePeak):
            self.reference.append(reference)

    def __post_init__(self):
        if self.normalizationFactor == 1.0:
            information_NormalizationFactor()
