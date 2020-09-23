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
from modules.BaseReader import BaseReader

# Enums
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC

# constants
from GLOBAL_CONSTANTS import EXPORT_TIMESTAMP

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
        # TODO: docstring
        self.dialect = self.DIALECT_CSV["name"]
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["CSV_DATA_COLUMN"]
        self.subKwargs = {"timeFormat": EXPORT_TIMESTAMP}

        # default batch columns must be the value of an CHC.element.
        self.defaultBatchYColumn = CHC.PEAK_AREA.value
        self.defaultBatchXColumn = CHC.HEADER_INFO.value

    def get_header(self, row:list)->tuple:
        """
        Extracts the header of an exported (csv, and spk) file.


        Parameters
        ----------
        row: list
            Required. The row of the file containing the header information.

        Returns
        -------
        date, time: str, str
            The date and the time of the measurement of the spectrum.

        """
        _, date, time = row[0].split()
        return (date, time)

    def preprocess(self, fReader, **kwargs):
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

        # Iterate until data, or Batchmarker is found.
        for row in fReader:
            cell = row[0]

            if self.MARKER["DATA"] in cell:
                break;
            elif self.MARKER["BATCH"] in cell:
                # A general issue might be to open the batchfile with excel or
                # something similar, because the program may use a different
                # dialect to save it again if changes were made.
                # Hint:
                    # Raises IndexError if columnYData cannot find the header.
                    # Can be handled by a different dialect (uses ',' as separator).

                # Get the column with respect to the header.
                xColumnName = self.defaultBatchXColumn
                yColumnName = kwargs.get("columnValue", self.defaultBatchYColumn)
                self.xColumn, self.yColumn = handle_batch_columns(row, xColumnName, yColumnName)
                break


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