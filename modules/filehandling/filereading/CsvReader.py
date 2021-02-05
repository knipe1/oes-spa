#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:11:22 2020

@author: Hauke Wernecke
"""

# standard libs

# third-party libs

# local modules/libs
from modules.filehandling.filereading.BaseReader import BaseReader

# Enums

# constants


class CsvReader(BaseReader):

    ### __Methods__

    def __init__(self):
        # Init baseclass providing defaults and config.
        super().__init__()
        self.__post_init__()

    def __post_init__(self):
        self.set_csv_defaults()


    ### Methods

    def set_csv_defaults(self):
        self.dialect = self.csvDialect
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["CSV_DATA_COLUMN"]
