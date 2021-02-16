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
from modules.filehandling.fileframework import FileFramework
import modules.universal as uni

# Enums

class BaseReader(FileFramework):

    ### __Methods__

    def __init__(self):
        super().__init__(filename=None)
        self.set_defaults()

    ### methods

    def set_defaults(self):
        # dialect
        self.dialect = self.spectralDialect
        # Column indeces
        self.xColumn = None
        self.yColumn = None
        # subKwargs
        self.subKwargs = {}
        self.data = []


    def add_xy_to_data(self, xy):
        self.data.append(xy)

    def readout_file(self, fReader, **kwargs)->dict:

        marker = self.MARKER["HEADER"]

        # data = []
        parameter = {}

        for line in fReader:
            markerElement, xDataElement, yDataElement = self.get_information(line)

            if self.is_data(xDataElement, yDataElement):
                # data.append((xDataElement, yDataElement))
                self.add_xy_to_data((xDataElement, yDataElement))
            elif self.contain_marker(marker, markerElement):
                timeInfo = self.get_time_info(markerElement)
            else:
                self.handle_additional_information(markerElement=markerElement, line=line, parameter=parameter, **kwargs)

        try:
            information = self.join_information(timeInfo, self.data, parameter)
        except UnboundLocalError:
            information = self.join_information(None, None)

        return information


    def handle_additional_information(self, **kwargs)->None:
        # No additional information by default. Child classes can introduce specific methods.
        return


    def get_information(self, line)->(str, str, str):
        try:
            markerElement = line[0]
        except IndexError:
            # Skip blank lines
            markerElement = None

        try:
            xDataElement = line[self.xColumn]
            yDataElement = line[self.yColumn]
        except IndexError:
            xDataElement = None
            yDataElement = None

        return markerElement, xDataElement, yDataElement


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
            xData = convert_to_float_or_time(xyData[:, 0])
            yData = convert_to_float_or_time(xyData[:, 1])
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


    def is_data(self, *elements:str)->bool:
        try:
            for element in elements:
                float(element)
        except (ValueError, TypeError):
            return False
        return True


    def contain_marker(self, marker:str, element:str):
        try:
            return (marker in element)
        except TypeError:
            return False

def convert_to_float_or_time(dataColumn:np.ndarray):
    try:
        dataColumn = np.array(dataColumn, dtype=float)
    except ValueError:
        dataColumn = np.array(dataColumn, dtype=object)
        for idx, element in enumerate(dataColumn):
            dataColumn[idx] = uni.timestamp_from_string(element)

    return dataColumn


def select_xyData(data:list, line:list, xColumn:int, yColumn:int)->tuple:
    try:
        xyData = (line[xColumn], line[yColumn])
        data.append(xyData)
    except IndexError:
        pass
