#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 11:27:29 2020

@author: hauke
"""

# standard libs
import numpy as np

# third-party libs

# local modules/libs
# FileFramework: base class.
from modules.FileFramework import FileFramework
import modules.Universal as uni

# Enums

class BaseReader(FileFramework):

    ### Properties

    # These are default values and may be overwritten in subclasses.
    @property
    def dialect(self):
        return self._dialect

    @dialect.setter
    def dialect(self, dialectname):
        self._dialect = dialectname

    @property
    def xyColumn(self):
        return self.xColumn, self.yColumn

    @property
    def xColumn(self):
        return self._xColumn

    @xColumn.setter
    def xColumn(self, columnIndex:int):
        self._xColumn = columnIndex

    @property
    def yColumn(self):
        return self._yColumn

    @yColumn.setter
    def yColumn(self, columnIndex:int):
        self._yColumn = columnIndex


    ### __Methods__

    def __init__(self):
        super().__init__(filename=None)
        self.set_defaults()

    ### methods

    def set_defaults(self):
        # dialect
        self.dialect = self.DIALECT["name"]
        # Column indeces
        self.xColumn = None
        self.yColumn = None
        # subKwargs
        self.subKwargs = {}


    def list_to_2column_array(self, xyData:list)->np.ndarray:
        xyData = np.array(xyData)
        try:
            xData = convert_to_float_or_time(xyData[:, 0])
            yData = convert_to_float_or_time(xyData[:, 1])
            xyData = np.array((xData, yData)).transpose()
        except IndexError:
            self.logger.warning("No valid x- and y-data given. Empty data?!")
        except:
            return

        return xyData


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


def is_floatable(*elements:str)->bool:
    try:
        for element in elements:
            float(element)
    except (ValueError, TypeError):
        return False
    return True
