#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 14:56:33 2021

@author: hauke
"""


# standard libs
import numpy as np
from datetime import datetime

# third-party libs
import sif_reader

# local modules/libs
from modules.filehandling.filereading.basereader import BaseReader
import modules.Universal as uni
import modules.dataanalysis.SpectrumHandler as SH

# Enums
from c_enum.ASC_PARAMETER import ASC_PARAMETER as ASC

# constants

class SifReader(BaseReader):

    ### Properties


    ### __Methods__

    def __init__(self):
        # Init baseclass providing defaults and config.
        super().__init__()
        self.__post_init__()

    def __post_init__(self):
        pass


    ### Methods

    def readout_file(self, fReader=None, **kwargs)->dict:
        """Parameter 'fReader' only required to have the same signature across reader."""
        filename = kwargs["filename"]
        file = sif_reader.np_open(filename)
        yData = file[0].flatten()
        parameter = file[1]
        xData = np.arange(1, yData.size+1)
        cali = parameter['Calibration_data']
        xData = cali[0] + xData * cali[1] + np.power(xData, 2) * cali[2] + np.power(xData, 3) * cali[3]

        timeInfo_ms = parameter['ExperimentTime']
        timeInfo = datetime.fromtimestamp(timeInfo_ms)
        parameter['ExperimentTime'] = uni.timestamp_to_string(timeInfo)
        parameter[ASC.WL.value] = np.round(SH.get_center(xData), 3)
        information = self.join_information(timeInfo, np.array([xData, yData]).T, parameter)
        return information
