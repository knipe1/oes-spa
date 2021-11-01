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
from datetime import datetime

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
    TIME_NOT_SET = "Not set!"

    MARKER  = {
        "BATCH": "Filename",
        "HEADER": "Date",
    }

    # Properties

    @property
    def timeInfo(self):
        return self._timestamp

    @timeInfo.setter
    def timeInfo(self, timestamp:datetime):
        if not timestamp:
            timestamp = self.TIME_NOT_SET
        self._timestamp = timestamp


    @property
    def fileinformation(self):
        return (self.filename, self.timeInfo)


    ## __methods__

    def __init__(self, filename:str)->None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self.filename = filename
        self.timeInfo = None
        self.data = None


    def __eq__(self, other):
        try:
            isEqual = (self.fileinformation == other.fileinformation)
        except AttributeError:
            # If compared with another type, that type has no header attribute.
            isEqual = False
        return isEqual


    def __repr__(self)->str:
        return self.__class__.__name__


    ## properties

    @property
    def spectralDialect(self):
        return DIALECT_SPECTRAL.name


    @property
    def csvDialect(self):
        return DIALECT_CSV.name
