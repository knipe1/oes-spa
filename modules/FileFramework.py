#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for general purposes regarding read and write operations

Register a common  dialect and
defines the configurations

@author: Hauke Wernecke
"""

# standard libs
import csv

# local modules/libs
from ConfigLoader import ConfigLoader
from Logger import Logger


class FileFramework:

    # Load the configuration for import, export and further properties.
    # TODO: Use Properties?
    config = ConfigLoader()
    EXPORT = config.EXPORT
    IMPORT = config.IMPORT
    MARKER = config.MARKER
    DIALECT = config.DIALECT
    DIALECT_CSV = config.DIALECT_CSV
    DATA_STRUCTURE = config.DATA_STRUCTURE
    TIMESTAMP = config.TIMESTAMP


    def __init__(self, filename):
        # set up the logger
        self.logger = Logger(__name__)

        self.filename = filename

        # Register different dialects for different filetypes.
        csv.register_dialect(self.DIALECT["name"],
                             delimiter = self.DIALECT["delimiter"],
                             quoting = self.DIALECT["quoting"])
        csv.register_dialect(self.DIALECT_CSV["name"],
                             delimiter = self.DIALECT_CSV["delimiter"],
                             quoting = self.DIALECT_CSV["quoting"])

        # set default dialect.
        self.dialect = self.DIALECT["name"]



# TODO: testcode to evaluate usage of datetime lib
# from datetime import datetime

# stamp = "30.11.2018 16:14:14"

# format_date = "%d.%m.%Y"
# format_time = "%H:%M:%S"
# test = datetime.strptime(stamp, format_date + " " + format_time)
# print(test.strftime(format_date))
# print(test.strftime(format_time))