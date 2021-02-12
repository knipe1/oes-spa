#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for general purposes regarding read and write operations.

@author: Hauke Wernecke
"""

# standard libs
import csv
import logging
from collections import namedtuple

# local modules/libs


# dialects
Dialect =  namedtuple("Dialect", ["name", "delimiter", "quoting"])

DIALECT_SPECTRAL = Dialect("spectral", delimiter="\t", quoting=csv.QUOTE_MINIMAL)
DIALECT_CSV = Dialect("csv", delimiter=",", quoting=csv.QUOTE_MINIMAL)

DIALECTS = [DIALECT_SPECTRAL,
            DIALECT_CSV,]

for dia in DIALECTS:
    csv.register_dialect(dia.name, quoting = dia.quoting, delimiter = dia.delimiter)


class FileFramework:

    # constants
    MARKER  = {"BATCH": "Filename",
              "DATA": "Data",
              "HEADER": "Date",}

    DATA_STRUCTURE = {"PIXEL_COLUMN": 0,
                      "ASC_DATA_COLUMN": 1,
                      "CSV_DATA_COLUMN": 1,
                      "SPK_DATA_COLUMN": 3,}


    ## __methods__

    def __init__(self, filename:str)->None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self.filename = filename


    def __repr__(self)->str:
        return self.__class__.__name__


    ## properties

    @property
    def spectralDialect(self):
        return DIALECT_SPECTRAL.name


    @property
    def csvDialect(self):
        return DIALECT_CSV.name
