#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 10:29:05 2020

@author: Hauke Wernecke
"""

# standard libs
import pandas as pd
import numpy as np
from datetime import datetime

# third-party libs

# local modules/libs
from .basereader import BaseReader
import modules.universal as uni

# Enums
from c_enum.data_column import DATA_COLUMN

# constants
DATETIME_MARKER = "Date and Time"
ASC_TIMESTAMP = '%a %b %d %H:%M:%S.%f %Y'
HEADER_X_DATA = "Pixel"
HEADER_Y_DATA = "Intensity"


class AscReader(BaseReader):


    def _set_columns(self):
        self.xColumn = DATA_COLUMN.PIXEL_COLUMN.value
        self.yColumn = DATA_COLUMN.ASC_DATA_COLUMN.value


    def readout_file(self, filename:str)->dict:

        dfFile = pd.read_csv(
            filename,
            names = (HEADER_X_DATA, HEADER_Y_DATA),
            header = None,
            usecols = [self.xColumn, self.yColumn],
            dialect = self.dialect,
            skip_blank_lines = True,
        )

        self.data = self.data_from_DataFrame(dfFile)
        parameter = self.parameter_from_DataFrame(dfFile)
        timeInfo = self.get_time_info(parameter)

        information = self.join_information(timeInfo, self.data, parameter)
        return information


    def data_from_DataFrame(self, df:pd.DataFrame)->np.ndarray:
        return df[df[HEADER_Y_DATA].notna()].to_numpy(dtype=float)


    def parameter_from_DataFrame(self, df:pd.DataFrame)->dict:
        rawParameter = df[df[HEADER_Y_DATA].isna()].to_numpy().T[0]
        parameter = {descriptor:value for descriptor, value in map(asc_separate_parameter, rawParameter)}
        return parameter


    def get_time_info(self, parameter:str)->datetime:
        element = parameter[DATETIME_MARKER]
        try:
            timestamp = uni.timestamp_from_string(element, ASC_TIMESTAMP)
        except ValueError:
            return None
        return timestamp


### module-level functions

def asc_separate_parameter(raw:str)->(str, str):
    """
    Separates the description and the value of a parameter of a .asc-file.

    Returns
    -------
    description : str
        Description of the parameter.
    value : str
        Value of the parameter.
    """

    # Split uses the first ":", because the value may contain one as well.
    description, value = raw.split(":", 1)
    value = value.strip()
    return (description, value)
