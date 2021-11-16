#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 11:27:29 2020

@author: hauke
"""

# standard libs
import numpy as np
from datetime import datetime

# third-party libs

# local modules/libs
# FileFramework: base class.
from ..fileframework import FileFramework
import modules.universal as uni

# Enums
from c_enum.data_column import DATA_COLUMN

class BaseReader(FileFramework):

    ### __Methods__

    def __init__(self):
        super().__init__(filename=None)
        self.set_defaults()

    ### methods

    def set_defaults(self):
        # dialect
        self.dialect = self.spectralDialect
        self.set_columns()
        # subKwargs
        self.subKwargs = {}
        self.data = []


    def set_columns(self):
        self.xColumn = None
        self.yColumn = None


    def join_information(self, timeInfo:str, data:list, parameter:dict=None)->dict:

        if data is not None:
            data = self.list_to_2column_array(data)

        information = {}
        information["timeInfo"] = timeInfo
        information["data"] = data
        information["parameter"] = parameter or {}
        return information



    def list_to_2column_array(self, xyData:list)->np.ndarray:
        xyData = np.array(xyData)
        try:
            # Note for x-data: float for pixels, time otherwise
            xData = uni.convert_to_float_or_time(xyData[:, 0])
            yData = uni.convert_to_float_or_time(xyData[:, 1])
            xyData = np.array((xData, yData)).transpose()
        except IndexError:
            self._logger.warning("No valid x- and y-data given. Empty data?!")
        except Exception:
            return None

        return xyData


    def get_time_info(self, element:str)->datetime:
        try:
            _, date, time = element.split()
            strTime = date + " " + time
            timestamp = uni.timestamp_from_string(strTime)
        except ValueError:
            return None

        return timestamp
