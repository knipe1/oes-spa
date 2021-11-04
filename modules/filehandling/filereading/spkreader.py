#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:11:22 2020

@author: Hauke Wernecke
"""

# standard libs

# third-party libs

# local modules/libs
from .basereader import BaseReader

# Enums
import pandas as pd

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
        self.dialect = self.spectralDialect
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["SPK_DATA_COLUMN"]


    def readout_file(self, filename:str)->dict:

        timeInfo = pd.read_csv(filename, dialect=self.dialect, nrows=1, header=None).loc[0,0]
        timeInfo = self.get_time_info(timeInfo)

        dfFile = pd.read_csv(filename,
                              header = None,
                              usecols = [self.xColumn, self.yColumn],
                              skiprows = 3,
                              dialect = self.dialect,
                              skip_blank_lines = True)
        self.data = dfFile.to_numpy()

        information = self.join_information(timeInfo, self.data)
        return information
