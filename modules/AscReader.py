#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 10:29:05 2020

@author: Hauke Wernecke
"""

# standard libs

# third-party libs

# local modules/libs
from modules.BaseReader import BaseReader, is_floatable, select_xyData
import modules.Universal as uni

# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE

# constants
from modules.Universal import EXPORT_TIMESTAMP
EXPORT_DATE, EXPORT_TIME = EXPORT_TIMESTAMP.split(" ")
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

    def set_asc_defaults(self):
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["ASC_DATA_COLUMN"]
        self.type = EXPORT_TYPE.SPECTRUM


    def readout_file(self, fReader)->dict:

        marker = self.MARKER["HEADER"]

        data = []
        parameter = {}

        for line in fReader:
            try:
                markerElement = line[0]
            except IndexError:
                # Skip blank lines
                continue

            try:
                xDataElement = line[self.xColumn]
                yDataElement = line[self.yColumn]
            except IndexError:
                xDataElement = None
                yDataElement = None

            if is_floatable(xDataElement, yDataElement):
                select_xyData(data, line, self.xColumn, self.yColumn)
            elif marker in markerElement:
                header = self.get_header(line)
            elif len(line) == 1:
                try:
                    name, value = asc_separate_parameter(line)
                except ValueError:
                    continue
                parameter[name] = value

        data = self.list_to_2column_array(data)

        information = {}
        information["header"] = header
        information["data"] = data
        information["parameter"] = parameter
        return information


    def get_header(self, element:list)->tuple:
        """
        Extracts the header of an .asc file.

        Parameters
        ----------
        row: list
            The row of the file containing the header information.

        Returns
        -------
        date, time: (str, str)
            The date and the time of the measurement of the spectrum.

        """

        try:
            _, strTime = asc_separate_parameter(element)
            timestamp = uni.timestamp_from_string(strTime, ASC_TIMESTAMP)
        except ValueError:
            return (None, None)

        # Format the timestamp according to the 'export' time format.
        date = uni.timestamp_to_string(timestamp, EXPORT_DATE)
        time = uni.timestamp_to_string(timestamp, EXPORT_TIME)

        return (date, time)



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


