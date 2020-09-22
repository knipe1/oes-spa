#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 11:27:29 2020

@author: hauke
"""

# standard libs

# third-party libs

# local modules/libs
# FileFramework: base class.
from modules.FileFramework import FileFramework

# Enums

class ConfigReader(FileFramework):

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

    # Timestamp formats
    @property
    def ascTimestampformat(self):
        return self.TIMESTAMP["ASC"]

    @property
    def exportTimestampformat(self):
        return self.TIMESTAMP["EXPORT"]

    @property
    def exportDateformat(self):
        return self._dateFormat

    @property
    def exportTimeformat(self):
        return self._timeFormat


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
        # timeformats
        self._dateFormat, self._timeFormat = self.exportTimestampformat.split(" ")
        # subKwargs
        self.subKwargs = {}