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
# BaseReader: base class.
from modules.filehandling.filereading.basereader import BaseReader
# further modules
import modules.Universal as uni

# enums (alphabetical order)
from c_enum.ASC_PARAMETER import ASC_PARAMETER as ASC
from c_enum.CHARACTERISTIC import CHARACTERISTIC as CHC
from c_enum.ERROR_CODE import ERROR_CODE as ERR
from c_enum.SUFFICES import SUFFICES as SUFF

# constants
from modules.Universal import EXPORT_TIMESTAMP


class BaReader(BaseReader):

    ### __Methods__

    def __init__(self):
        # Init baseclass providing defaults and config.
        super().__init__()
        self.__post_init__()

    def __post_init__(self):
        self.set_ba_defaults()


    ### Methods

    def set_ba_defaults(self):
        self.dialect = self.csvDialect
        self.xColumn = 0
        self.yColumn = 0
        self.peakColumn = 0
        self.timeFormat = EXPORT_TIMESTAMP

        # default batch columns must be the value of an CHC.element.
        self.defaultBatchYColumn = CHC.PEAK_AREA.value
        self.defaultBatchXColumn = CHC.HEADER_INFO.value
        self.nameColumn = CHC.PEAK_NAME.value
        self.data = {}


    def add_xy_to_data(self, xy):
        if self.currentPeakName in self.data.keys():
            self.data[self.currentPeakName].append(xy)
        else:
            self.data[self.currentPeakName] = [xy]


    def get_information(self, line, **kwargs)->(str, str, str):

        # Determine the peak name if possible
        try:
            peakName = line[self.peakColumn]
            self.currentPeakName = peakName
        except IndexError:
            self.currentPeakName = None

        markerElement, xDataElement, yDataElement = super().get_information(line)
        return markerElement, xDataElement, yDataElement


    def is_data(self, xDataElement:str, yDataElement:str)->bool:
        try:
            uni.timestamp_from_string(xDataElement)
            is_xData = True
        except (TypeError, ValueError):
            is_xData = super().is_data(xDataElement)

        is_yData = super().is_data(yDataElement)

        return (is_xData and is_yData)


    def handle_additional_information(self, **kwargs)->None:
        batchMarker = self.MARKER["BATCH"]
        line = kwargs.get("line")
        if not self.contain_marker(batchMarker, line):
            return

        line = kwargs.get("line")
        xColumnName = self.defaultBatchXColumn
        yColumnName = kwargs.get("columnValue", self.defaultBatchYColumn)
        self.xColumn, self.yColumn, self.peakColumn = self.determine_batch_column_indeces(line, xColumnName, yColumnName, self.nameColumn)


    def join_information(self, timeInfo:str, data:dict, parameter:dict=None)->dict:
        try:
            peaks = data.keys()
        except AttributeError:
            peaks = {}

        for peak in peaks:
            data[peak] = super().list_to_2column_array(data[peak])

        information = {}
        information["timeInfo"] = timeInfo
        information["data"] = data
        information["parameter"] = parameter or {}
        return information


    def determine_batch_column_indeces(self, dataHeader:list, xColumnName:str, yColumnName:str, nameColumn:str)->(int, int, int):
        """


        Parameters
        ----------
        dataHeader : list
            Contains the header information of the batch file.
        xColumnName : str
            Name of the header information, which contains the y-data.
        yColumnName : str
            Name of the header information, which contains the y-data.
        nameColumn : str
            Name of the header information, which contains the peak information.

        Returns
        -------
        xColumn : int
            Index of the column which contains the x-values.
        yColumn : int
            Index of the column which contains the y-values.
        peakColumn : int
            Index of the column which contains the peak name.

        """
        # Filter allows to search for characteristic value, because
        # the specific name of that peak is added to the static value.
        wildcard = "*"
        wildColumnName = yColumnName + wildcard
        yColumn = dataHeader.index(fnmatch.filter(dataHeader, wildColumnName)[0])

        try:
            xColumn = dataHeader.index(xColumnName)
        except ValueError:
            xColumn = self.xColumn

        try:
            peakColumn = dataHeader.index(nameColumn)
        except ValueError:
            peakColumn = self.peakColumn

        return xColumn, yColumn, peakColumn
