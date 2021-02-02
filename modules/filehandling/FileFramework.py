#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for general purposes regarding read and write operations.

@author: Hauke Wernecke
"""

# standard libs
import csv
import logging

# local modules/libs
from loader.ConfigLoader import ConfigLoader



class FileFramework:

    # Configuration.
    config = ConfigLoader()

    # constants
    MARKER  = {"BATCH": "Filename",
              "DATA": "Data",
              "HEADER": "Date",}

    DATA_STRUCTURE = {"PIXEL_COLUMN": 0,
                      "ASC_DATA_COLUMN": 1,
                      "CSV_DATA_COLUMN": 1,
                      "SPK_DATA_COLUMN": 3,}

    DIALECT = {"name": "spectral_data",
               "delimiter": "\t",
               "quoting": csv.QUOTE_MINIMAL,}

    DIALECT_CSV = {"name": "csv_data",
                   "delimiter": ",",
                   "quoting": csv.QUOTE_MINIMAL,}


    def __init__(self, filename, **kwargs):
        # Set up the logger.
        name = kwargs.get("name", __name__)
        self._logger = logging.getLogger(name)

        self.filename = filename
        self.register_dialects()


    @property
    def spectralDialect(self):
        return self.DIALECT["name"]


    @property
    def csvDialect(self):
        return self.DIALECT_CSV["name"]


    def register_dialects(self):
        csv.register_dialect(self.DIALECT["name"],
                             delimiter = self.DIALECT["delimiter"],
                             quoting = self.DIALECT["quoting"])
        csv.register_dialect(self.DIALECT_CSV["name"],
                             delimiter = self.DIALECT_CSV["delimiter"],
                             quoting = self.DIALECT_CSV["quoting"])
