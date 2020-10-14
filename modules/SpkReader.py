#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:11:22 2020

@author: Hauke Wernecke
"""

# standard libs
import numpy as np

# third-party libs

# local modules/libs
from modules.BaseReader import BaseReader, is_floatable, select_xyData

# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE
from custom_types.ERROR_CODE import ERROR_CODE as ERR


class SpkReader(BaseReader):

    ### Properties

    ### __Methods__

    def __init__(self):
        # Init baseclass providing defaults and config.
        super().__init__()
        self.__post_init__()

    def __post_init__(self):
        self.set_spk_defaults()


    ### Methods

    def set_spk_defaults(self):
        # TODO: docstring
        self.dialect = self.DIALECT["name"]
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["SPK_DATA_COLUMN"]
        self.type = EXPORT_TYPE.SPECTRUM


    def readout_file(self, fReader)->dict:

        marker = self.MARKER["HEADER"]
        data = []

        for line in fReader:
            try:
                element = line[0]
            except IndexError:
                # Skip blank lines
                continue

            if is_floatable(element):
                data.append(select_xyData(line, self.xColumn, self.yColumn))
            elif marker in element:
                _, date, time = element.split()
                header = (date, time)

        data = self.list_to_2column_array(data)

        information = {}
        information["header"] = header
        information["data"] = data
        return information

