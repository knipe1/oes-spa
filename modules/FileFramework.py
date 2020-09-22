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
    EXPORT = config.EXPORT
    IMPORT = config.IMPORT
    DIALECT = config.DIALECT
    DIALECT_CSV = config.DIALECT_CSV
    DATA_STRUCTURE = config.DATA_STRUCTURE
    TIMESTAMP = config.TIMESTAMP

    # constants
    MARKER  = {"BATCH": "Filename",
              "DATA": "Data",
              "HEADER": "Date",}


    def __init__(self, filename):
        # Set up the logger.
        self.logger = Logger(__name__)

        self.filename = filename
        self.register_dialects()
        self.dialect = None


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