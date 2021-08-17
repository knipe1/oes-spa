#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 16:48:57 2020

@author: hauke
"""

# standard libs
import logging
import numpy as np

# third-party libs

# local modules/libs
from exception.CalibrationError import CalibrationError

# constants
NO_ITERATION = 3
MAX_SHIFT_nm = 0.3



class Calibration():

    ### Properties


    ### __Methods__

    def __init__(self, calibrationFile:str)->None:
        self._logger = logging.getLogger(self.__class__.__name__)

        self._shift = 0.0

        self.calibrationPeaks = np.loadtxt(calibrationFile)[:, 0]
        self.noPeaks = len(self.calibrationPeaks)


    ### Methods
    def calibrate(self, xData:np.ndarray, yData:np.ndarray)->np.ndarray:
        for _ in range(NO_ITERATION):
            xData = self.calibrate_data(xData, yData)
        return xData, self._shift


    def calibrate_data(self, xData:np.ndarray, yData:np.ndarray)->np.ndarray:

        # find indeces of the reference peaks in the proccessed data
        wlIndex, maxShift = self.find_indeces_and_max_shift(xData)
        if any(wlIndex + maxShift > xData.size) or any(wlIndex - maxShift < 0) or maxShift == 0:
            raise CalibrationError("Calibration peaks out of spectral range!")

        calibrationIntensities = np.zeros(shape=(self.noPeaks, 2*maxShift+1))
        for idx in range(-maxShift, maxShift+1):
            for ref in range(self.noPeaks):
                intensity = yData[wlIndex[ref] + idx]
                idxOffset = idx + maxShift
                calibrationIntensities[ref, idxOffset] = intensity

        summedIntensities = calibrationIntensities.sum(axis=0)

        shift = summedIntensities.argmax() - maxShift
        absShift = (self.calibrationPeaks - xData[wlIndex-shift]).mean()
        self._shift += absShift

        shiftedData = xData - absShift
        return shiftedData


    def find_indeces_and_max_shift(self, xData:np.ndarray)->np.ndarray:
        wlIndex = np.zeros((self.noPeaks), dtype=int)
        maxShift = 0
        for i, wl in enumerate(self.calibrationPeaks):
            wlIndex[i] = self.find_index_with_closest_value(xData, wl)
            # determine the range of the convolution
            idxShift = self.find_index_with_closest_value(xData, (wl + MAX_SHIFT_nm))
            maxShift = max(idxShift-wlIndex[i], maxShift)
        return wlIndex, maxShift


    @staticmethod
    def find_index_with_closest_value(arr:np.ndarray, value:float)->int:
        index = np.abs(arr - value).argmin()
        return index
