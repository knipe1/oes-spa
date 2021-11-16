#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:11:22 2020

@author: Hauke Wernecke
"""

# standard libs
import pandas as pd

# third-party libs

# local modules/libs
from .basereader import BaseReader

# Enums
from c_enum.data_column import DATA_COLUMN

class SpkReader(BaseReader):


    ### Methods

    def _set_columns(self):
        self.xColumn = DATA_COLUMN.PIXEL_COLUMN.value
        self.yColumn = DATA_COLUMN.SPK_DATA_COLUMN.value


    def readout_file(self, filename:str)->dict:

        timeInfo = pd.read_csv(filename, dialect=self.dialect, nrows=1, header=None).loc[0,0]
        timeInfo = self.get_time_info(timeInfo)

        dfFile = pd.read_csv(
            filename,
            header = None,
            usecols = [self.xColumn, self.yColumn],
            skiprows = 3,
            dialect = self.dialect,
            skip_blank_lines = True
        )
        self.data = dfFile.to_numpy()

        information = self.join_information(timeInfo, self.data)
        return information
