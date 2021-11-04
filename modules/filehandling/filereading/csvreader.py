#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:11:22 2020

@author: Hauke Wernecke
"""

# standard libs
import pandas as pd

# third-party libs

# local modules/libs
from .basereader import BaseReader

# Enums

# constants
HEADER_X_DATA = "X"
HEADER_Y_DATA = "Y"


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


    def readout_file(self, filename:str):

        dfFile = pd.read_csv(filename,
                            names = (HEADER_X_DATA, HEADER_Y_DATA),
                            usecols = [self.xColumn, self.yColumn],
                            dialect = self.dialect,
                            skip_blank_lines = True,
                            )

        # starts with a number
        isnumericIndex = dfFile.iloc[:, 0].str.contains("(^[0-9])")

        data = dfFile[isnumericIndex]
        self.data = data.to_numpy(dtype=float)

        rawParameter = dfFile[~isnumericIndex].to_numpy()
        parameter = {key:value for key, value in rawParameter[1:-1]}

        timeInfo = self.get_time_info(rawParameter[0, 0])

        information = self.join_information(timeInfo, self.data, parameter)
        return information
