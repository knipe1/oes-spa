#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for general purposes regarding read and write operations.

@author: Hauke Wernecke
"""

# standard libs
import csv

# local modules/libs
from ConfigLoader import ConfigLoader
from Logger import Logger



class FileFramework:

    # Configuration.
    config = ConfigLoader()
    IMPORT = config.IMPORT

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


    def __init__(self, filename):
        # Set up the logger.
        self.logger = Logger(__name__)

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



# TODO: testcode to evaluate usage of datetime lib
# from datetime import datetime

# stamp = "30.11.2018 16:14:14"

# format_date = "%d.%m.%Y"
# format_time = "%H:%M:%S"
# test = datetime.strptime(stamp, format_date + " " + format_time)
# print(test.strftime(format_date))
# print(test.strftime(format_time))