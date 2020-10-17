#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:11:22 2020

@author: Hauke Wernecke
"""

# standard libs
# fnmatch: Unix filename pattern matching (https://docs.python.org/3/library/fnmatch.html)
import fnmatch

# third-party libs

# local modules/libs
from modules.BaseReader import BaseReader, select_xyData

# Enums
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC
from custom_types.EXPORT_TYPE import EXPORT_TYPE

# constants
from modules.Universal import EXPORT_TIMESTAMP

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
        self.dialect = self.DIALECT_CSV["name"]
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["CSV_DATA_COLUMN"]
        self.subKwargs = {"timeFormat": EXPORT_TIMESTAMP}
        self.type = EXPORT_TYPE.SPECTRUM

        # default batch columns must be the value of an CHC.element.
        self.defaultBatchYColumn = CHC.PEAK_AREA.value
        self.defaultBatchXColumn = CHC.HEADER_INFO.value

    def readout_file(self, fReader, **kwargs)->dict:

        marker = self.MARKER["HEADER"]

        data = []

        for line in fReader:
            try:
                markerElement = line[0]
            except IndexError:
                # Skip blank lines
                continue

            if marker in markerElement:
                header = self.get_header(markerElement)
            elif self.MARKER["BATCH"] in markerElement:
                # A general issue might be to open the batchfile with excel or
                # something similar, because the program may use a different
                # dialect to save it again if changes were made.
                # Hint:
                    # Raises IndexError if columnYData cannot find the header.
                    # Can be handled by a different dialect (uses ',' as separator).
                self.type = EXPORT_TYPE.BATCH
                xColumnName = self.defaultBatchXColumn
                yColumnName = kwargs.get("columnValue", self.defaultBatchYColumn)
                self.xColumn, self.yColumn = handle_batch_columns(line, xColumnName, yColumnName)
                data = self.get_data(fReader)
            elif self.MARKER["DATA"] in markerElement:
                self.type = EXPORT_TYPE.SPECTRUM
                data = self.get_data(fReader)

        data = self.list_to_2column_array(data)

        information = {}
        information["header"] = header
        information["data"] = data
        return information


    def get_header(self, element:list)->tuple:
        """
        Extracts the header of the given list 'element'.

        Returns
        -------
        date, time: (str, str)
            The date and the time of the measurement of the spectrum.

        """

        try:
            _, date, time = element.split()
        except ValueError:
            return (None, None)

        return (date, time)


    def get_data(self, fReader):
        data = []
        for line in fReader:
            select_xyData(data, line, self.xColumn, self.yColumn)
        return data


def handle_batch_columns(dataHeader:list, xColumnName:str, yColumnName:str)->(int, int):
    """


    Parameters
    ----------
    dataHeader : list
        Contains the header information of the batch file.
    columnName : str
        Name of the header information, which contains the y-data.

    Returns
    -------
    xColumn : int
        Index of the column which contains the x-values.
    yColumn : int
        Index of the column which contains the y-values.

    """
    # Filter allows to search for characteristic value, because
    # the specific name of that peak is added to the static value.
    wildcard = "*"
    wildColumnName = yColumnName + wildcard
    yColumn = dataHeader.index(fnmatch.filter(dataHeader, wildColumnName)[0])
    xColumn = dataHeader.index(xColumnName)

    return xColumn, yColumn


