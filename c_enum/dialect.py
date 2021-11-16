#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 14:01:13 2021

@author: hauke
"""

# standard libs
import csv
from dataclasses import dataclass


@dataclass(frozen=True)
class Dialect:
    name: str
    delimiter: str
    quoting: int

    def __post_init__(self):
        csv.register_dialect(self.name, quoting = self.quoting, delimiter = self.delimiter)


DIALECT_SPECTRAL = Dialect("spectral", delimiter="\t", quoting=csv.QUOTE_MINIMAL)
DIALECT_CSV = Dialect("csv", delimiter=",", quoting=csv.QUOTE_MINIMAL)
