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
from modules.BaseReader import BaseReader

# constants
from GLOBAL_CONSTANTS import ASC_TIMESTAMP, EXPORT_TIMESTAMP

EXPORT_DATE, EXPORT_TIME = EXPORT_TIMESTAMP.split(" ")

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

    def set_asc_defaults(self):
        # TODO: docstring
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["ASC_DATA_COLUMN"]


    def get_header(self, row:list)->tuple:
        """
        Extracts the header of an .asc file.

        Parameters
        ----------
        row: list
            Required. The row of the file containing the header information.

        Returns
        -------
        date, time: str, str
            The date and the time of the measurement of the spectrum.

        """
        _, timestamp = asc_separate_parameter(row)

        # Convert the given time string into date and time.
        timestamp = datetime.strptime(timestamp, ASC_TIMESTAMP)

        # Format the timestamp according to the 'export' time format.
        date = timestamp.strftime(EXPORT_DATE)
        time = timestamp.strftime(EXPORT_TIME)

        return (date, time)

    def get_parameter(self, fReader):
        """
        Read out the data of a .asc-file respective to its structure.

        Parameters
        ----------
        fReader : csv.reader-object
            Reader to iterate through the csv-file.

        Returns
        -------
        data: list
            Contain the pixel/intensity values.

        """

        parameter = {}

        # Gather the parameter.
        for row in fReader:
            try:
                name, value = asc_separate_parameter(row)
                parameter[name] = value
            except IndexError:
                # Break at the first blank row.
                break

        return parameter;


    def preprocess(self, fReader):
        # TODO: docstring
        for row in fReader:
            if len(row) != 0:
                break
        return



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