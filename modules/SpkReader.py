#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:11:22 2020

@author: Hauke Wernecke
"""

# standard libs
from datetime import datetime

# third-party libs

# local modules/libs
import modules.Universal as uni
from modules.BaseReader import BaseReader, is_floatable, select_xyData

# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE


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
        self.dialect = self.DIALECT["name"]
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["SPK_DATA_COLUMN"]
        self.type = EXPORT_TYPE.SPECTRUM


    def readout_file(self, fReader)->dict:

        marker = self.MARKER["HEADER"]
        data = []

        for line in fReader:
            try:
                markerElement = line[0]
            except IndexError:
                # Skip blank lines
                continue

            try:
                xDataElement = line[self.xColumn]
                yDataElement = line[self.yColumn]
            except IndexError:
                xDataElement = None
                yDataElement = None

            if is_floatable(xDataElement, yDataElement):
                select_xyData(data, line, self.xColumn, self.yColumn)
            elif marker in markerElement:
                timeInfo = self.get_time_info(markerElement)

        data = self.list_to_2column_array(data)

        information = {}
        information["timeInfo"] = timeInfo
        information["data"] = data
        return information


    def get_time_info(self, element:str)->datetime:
        try:
            _, date, time = element.split()
            strTime = date + " " + time
            timestamp = uni.timestamp_from_string(strTime)
        except ValueError:
            return None

        return timestamp
