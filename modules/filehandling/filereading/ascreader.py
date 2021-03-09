#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 10:29:05 2020

@author: Hauke Wernecke
"""

# standard libs
from datetime import datetime

# third-party libs

# local modules/libs
from modules.filehandling.filereading.basereader import BaseReader
import modules.universal as uni

# Enums
import pandas as pd
import numpy as np

# constants
ASC_TIMESTAMP = '%a %b %d %H:%M:%S.%f %Y'

class AscReader(BaseReader):

    ### Properties


    ### __Methods__

    def __init__(self):
        # Init baseclass providing defaults and config.
        super().__init__()
        self.__post_init__()

    def __post_init__(self):
        self.set_asc_defaults()


    ### Methods

    def set_asc_defaults(self)->None:
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["ASC_DATA_COLUMN"]


    def readout_file(self, fReader, **kwargs):
        filename = kwargs["filename"]

        test = pd.read_csv(filename,
                            names = ("Pixel", "Intensity"),
                            header = None,
                            usecols = [self.xColumn, self.yColumn],
                            dialect = self.dialect,
                            skip_blank_lines = True,
                            )

        testarray = test.to_numpy()
        params = np.isnan(np.asfarray(testarray[:, 1]))
        parameter = self.handle_additional_information_new(testarray[params][:, 0])
        self.data = np.asfarray(testarray[~params])
        timeInfo = self.get_time_info_new(parameter["Date and Time"])

        information = self.join_information(timeInfo, self.data, parameter)
        return information


    def handle_additional_information(self, **kwargs)->None:
        line = kwargs.get("line", [])
        if len(line) == 1:
            try:
                name, value = asc_separate_parameter(line)
            except ValueError:
                return
            parameter = kwargs.get("parameter")
            parameter[name] = value


    def handle_additional_information_new(self, pararray)->dict:
        parameter = {}
        for element in pararray:
            name, value = asc_separate_parameter_new(element)
            parameter[name] = value
        return parameter


    def get_time_info(self, element:str)->datetime:
        try:
            _, strTime = asc_separate_parameter([element])
            timestamp = uni.timestamp_from_string(strTime, ASC_TIMESTAMP)
        except ValueError:
            return None
        return timestamp


    def get_time_info_new(self, element:str)->datetime:
        try:
            # _, strTime = asc_separate_parameter([element])
            # timestamp = uni.timestamp_from_string(strTime, ASC_TIMESTAMP)
            timestamp = uni.timestamp_from_string(element, ASC_TIMESTAMP)
        except ValueError:
            return None
        return timestamp


### module-level functions

def asc_separate_parameter(row:list)->(str, str):
    """
    Separates the description and the value of a parameter of a .asc-file.

    Parameters
    ----------
    row : list
        The row of a file, e.g. readout by a csv.reader-object.

    Returns
    -------
    description : str
        Description of the parameter.
    value : str
        Value of the parameter.
    """

    # Split uses the first ":", because the value may contain one as well.
    description, value = row[0].split(":", 1)
    value = value.strip()
    return (description, value)

def asc_separate_parameter_new(row:list)->(str, str):
    """
    Separates the description and the value of a parameter of a .asc-file.

    Parameters
    ----------
    row : list
        The row of a file, e.g. readout by a csv.reader-object.

    Returns
    -------
    description : str
        Description of the parameter.
    value : str
        Value of the parameter.
    """

    # Split uses the first ":", because the value may contain one as well.
    description, value = row.split(":", 1)
    value = value.strip()
    return (description, value)
