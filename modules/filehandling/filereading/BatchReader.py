#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 22:06:55 2020

@author: hauke
"""



# standard libs
import csv
import numpy as np
from datetime import datetime
# fnmatch: Unix filename pattern matching (https://docs.python.org/3/library/fnmatch.html)
import fnmatch

# third-party libs

# local modules/libs
# FileFramework: base class.
from modules.filehandling.filereading.FileReader import FileReader
# specific subReader
from modules.filehandling.filereading.BaseReader import BaseReader
# further modules
import modules.Universal as uni

# enums (alphabetical order)
from custom_types.ASC_PARAMETER import ASC_PARAMETER as ASC
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC
from custom_types.ERROR_CODE import ERROR_CODE as ERR
from custom_types.SUFFICES import SUFFICES as SUFF

# constants
from modules.Universal import EXPORT_TIMESTAMP


class BatchReader(FileReader):

    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self.__post_init__(**kwargs)


    def __post_init__(self, **kwargs):
        self.set_defaults()
        self.read_file(**kwargs)


    def set_defaults(self):
        self.dialect = self.DIALECT_CSV["name"]
        self.xColumn = None
        self.yColumn = None
        self.timeFormat = EXPORT_TIMESTAMP

        # default batch columns must be the value of an CHC.element.
        self.defaultBatchYColumn = CHC.PEAK_AREA.value
        self.defaultBatchXColumn = CHC.HEADER_INFO.value
        self.nameColumn = CHC.PEAK_NAME.value


    def read_file(self, **kwargs)->ERR:

        with open(self.filename, 'r', newline='') as openFile:
            # Set up the reader (even if the file is something else than csv, because we use another dialect then).
            fReader = csv.reader(openFile, dialect=self.dialect)

            fileinformation = self.readout_file(fReader, **kwargs)
            self.timeInfo = fileinformation["timeInfo"]
            self.data = fileinformation["data"]
            self.parameter = fileinformation.get("parameter", {})


    def read_marker(self, line):
        marker = self.MARKER["HEADER"]

        markerElement = line[0]





def determine_batch_column_indeces(dataHeader:list, xColumnName:str, yColumnName:str)->(int, int):
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