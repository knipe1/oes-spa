#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:11:22 2020

@author: Hauke Wernecke
"""

# standard libs
import pandas as pd
import numpy as np
import datetime as dt

# third-party libs

# local modules/libs
from .basereader import BaseReader

# Enums
from c_enum.data_column import DATA_COLUMN
from c_enum.dialect import DIALECT_CSV

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
        self.dialect = DIALECT_CSV.name


    ### Methods


    def _set_columns(self):
        self.xColumn = DATA_COLUMN.PIXEL_COLUMN.value
        self.yColumn = DATA_COLUMN.CSV_DATA_COLUMN.value


    def readout_file(self, filename:str)->(str, np.ndarray, dict):

        dfFile = pd.read_csv(
            filename,
            names = (HEADER_X_DATA, HEADER_Y_DATA),
            usecols = [self.xColumn, self.yColumn],
            dialect = self.dialect,
            skip_blank_lines = True,
        )

        numericIndex = self.get_numerical_index(dfFile)

        self.data = self._get_data(dfFile, numericIndex)
        parameter, timeInfo = self._get_parameter_and_time(dfFile, numericIndex)

        return self.join_information(timeInfo, self.data, parameter)



    def _get_data(self, df:pd.DataFrame, index:pd.Series)->np.ndarray:
        return df[index].to_numpy(dtype=float)


    def _get_parameter_and_time(self, df:pd.DataFrame, index:pd.Series)->(dict, dt.datetime):
        rawParameter = df[~index].to_numpy()
        # Skip the first element (see. time), as well as the last (unused header information).
        parameter = {key:value for key, value in rawParameter[1:-1]}
        time = self.get_time_info(rawParameter[0, 0])
        return parameter, time


    @staticmethod
    def get_numerical_index(df:pd.DataFrame)->pd.Series:
        """Gets all the indeces with a numerical index."""
        return df.iloc[:, 0].str.contains("(^[0-9])")
