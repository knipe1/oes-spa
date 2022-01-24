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
from .basereader import BaseReader
import modules.universal as uni

# Enums
from c_enum.asc_parameter import ASC_PARAMETER as ASC

# constants
NAME_TIME = "ExperimentTime"
CALIBRATION_FACTORS = "Calibration_data"




class SifReader(BaseReader):

    ### Methods

    def readout_file(self, filename:str)->dict:
        intensities, parameter = sif_reader.np_open(filename)

        wavelength, intensities = self._format_and_calibrate(intensities, parameter)
        timeInfo = self._format_time(parameter)
        # Add the central wavelength as parameter.
        parameter[ASC.WL.value] = self._central_wavelength(wavelength)

        return self.join_information(timeInfo, np.array([wavelength, intensities]).T, parameter)


    def _format_time(self, parameter:dict)->str:
        """Formats the time in-place in parameter and also returns it."""
        timeInfo_ms = parameter[NAME_TIME]
        timeInfo = datetime.fromtimestamp(timeInfo_ms)
        parameter[NAME_TIME] = uni.timestamp_to_string(timeInfo)
        return timeInfo


    def _format_and_calibrate(self, intensities:np.ndarray, parameter:dict):
        """Formats the intensities and calibrate the wavelenght by specified parameter."""
        intensities = self._format_intensities(intensities)
        wavelength = self._calibrate(intensities, parameter)
        return wavelength, intensities


    def _format_intensities(self, intensities:np.ndarray)->np.ndarray:
        return intensities.flatten()


    def _calibrate(self, intensities:np.ndarray, parameter:dict):
        pixel = np.arange(1, intensities.size + 1)
        factors = parameter[CALIBRATION_FACTORS]
        return self._sif_calibration(pixel, factors)


    @staticmethod
    def _central_wavelength(wavelength:np.ndarray)->float:
        return np.round(uni.get_center(wavelength), 3)


    @staticmethod
    def _sif_calibration(pixel:np.ndarray, factors:list)->np.ndarray:
        data = (
            factors[0]
            + pixel * factors[1]
            + np.power(pixel, 2) * factors[2]
            + np.power(pixel, 3) * factors[3]
        )
        return data
