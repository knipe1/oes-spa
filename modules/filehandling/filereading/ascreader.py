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
import modules.Universal as uni

# Enums

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


    def handle_additional_information(self, **kwargs)->None:
        line = kwargs.get("line", [])
        if len(line) == 1:
            try:
                name, value = asc_separate_parameter(line)
            except ValueError:
                return
            parameter = kwargs.get("parameter")
            parameter[name] = value


    def get_time_info(self, element:str)->datetime:
        try:
            _, strTime = asc_separate_parameter([element])
            timestamp = uni.timestamp_from_string(strTime, ASC_TIMESTAMP)
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
