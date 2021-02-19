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
import modules.universal as uni
import modules.dataanalysis.spectrumhandler as SH

# Enums
from c_enum.asc_parameter import ASC_PARAMETER as ASC

# constants
NAME_TIME = "ExperimentTime"
CALIBRATION_FACTORS = "Calibration_data"

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
        yData, parameter = file[0], file[1]

        # Data handling.
        yData = yData.flatten()
        xData = np.arange(1, yData.size+1)
        factors = parameter[CALIBRATION_FACTORS]
        xData = self.self_calibration(xData, factors)

        # Parameter handling.
        timeInfo_ms = parameter[NAME_TIME]
        timeInfo = datetime.fromtimestamp(timeInfo_ms)
        parameter[NAME_TIME] = uni.timestamp_to_string(timeInfo)
        parameter[ASC.WL.value] = np.round(SH.get_center(xData), 3)

        information = self.join_information(timeInfo, np.array([xData, yData]).T, parameter)
        return information


    @staticmethod
    def self_calibration(rawData:np.ndarray, factors:list)->np.ndarray:
        data = (factors[0]
                + rawData * factors[1]
                + np.power(rawData, 2) * factors[2]
                + np.power(rawData, 3) * factors[3])
        return data
