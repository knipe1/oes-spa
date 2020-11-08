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
import modules.Universal as uni
from modules.filehandling.filereading.BaseReader import BaseReader

# Enums
from c_enum.CHARACTERISTIC import CHARACTERISTIC as CHC

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

        # default batch columns must be the value of an CHC.element.
        self.defaultBatchYColumn = CHC.PEAK_AREA.value
        self.defaultBatchXColumn = CHC.HEADER_INFO.value


    def handle_additional_information(self, **kwargs)->None:
        batchMarker = self.MARKER["BATCH"]
        markerElement = kwargs.get("markerElement")
        if not self.contain_marker(batchMarker, markerElement):
            return

        line = kwargs.get("line")
        xColumnName = self.defaultBatchXColumn
        yColumnName = kwargs.get("columnValue", self.defaultBatchYColumn)
        self.xColumn, self.yColumn = determine_batch_column_indeces(line, xColumnName, yColumnName)



    # def is_data(self, xDataElement:str, yDataElement:str)->bool:
    #     try:
    #         uni.timestamp_from_string(xDataElement)
    #         is_xData = True
    #     except (TypeError, ValueError):
    #         is_xData = super().is_data(xDataElement)

    #     is_yData = super().is_data(yDataElement)

    #     return (is_xData and is_yData)


    # def get_information(self, line, **kwargs)->(str, str, str):

    #     markerElement, xDataElement, yDataElement = super().get_information(line)

    #     peakName = kwargs.get("peakName")
    #     if (not peakName is None) and (peakName in line):
    #         return markerElement, xDataElement, yDataElement, peakName
    #     else:
    #         return markerElement, xDataElement, yDataElement




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


