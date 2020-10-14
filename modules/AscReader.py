#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 10:29:05 2020

@author: Hauke Wernecke
"""

# standard libs
import csv
import numpy as np

# third-party libs

# local modules/libs
from modules.BaseReader import BaseReader
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
                element = line[0]
            except IndexError:
                # Skip blank lines
                continue
            if is_floatable(element):
                data.append(line)
            elif marker in element:
                header = self.get_header(line)
            elif len(line) == 1:
                name, value = asc_separate_parameter(line)
                parameter[name] = value


        data = np.array(data, dtype=float)

        try:
            xData = data[:, self.xColumn]
            yData = data[:, self.yColumn]
            data = np.array((xData, yData)).transpose()
        except IndexError:
            self.logger.warning("No data found.")

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
        date, time: str, str
            The date and the time of the measurement of the spectrum.

        """

        try:
            _, strTime = asc_separate_parameter(element)
            # Convert the given time string into date and time.
            timestamp = uni.timestamp_from_string(strTime, ASC_TIMESTAMP)
        except ValueError:
            return (None, None)

        # Format the timestamp according to the 'export' time format.
        date = uni.timestamp_to_string(timestamp, EXPORT_DATE)
        time = uni.timestamp_to_string(timestamp, EXPORT_TIME)

        return (date, time)


    def get_parameter(self, fReader:csv.reader)->dict:
        """
        Read out the data of a .asc-file respective to its structure.

        Parameters
        ----------
        fReader : csv.reader-object
            Reader to iterate through the csv-file.

        Returns
        -------
        parameter: dict

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
            except ValueError:
                # Skip invalid parameter line.
                continue

        return parameter;

    def get_parameter_n(self, parameterContainer:set)->dict:
        parameter = {}
        for element in parameterContainer:
            try:
                name, value = asc_separate_parameter_n(element)
                parameter[name] = value
            except ValueError:
                # Skip invalid parameter
                continue
        return parameter

    def extract_data(self, data:list):
        data = np.array(data, dtype=float)
        return data


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

def asc_separate_parameter_n(element:str)->(str, str):
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
    description, value = element.split(":", 1)
    value = value.strip()
    return (description, value)

def is_floatable(element:str)->bool:
    try:
        float(element)
        return True
    except ValueError:
        return False