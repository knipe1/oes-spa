#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data processing module

Contains routines to convert raw data and obtain different parameters
"""

import numpy as np

from scipy import sparse
from scipy.sparse.linalg import spsolve
from peakutils import baseline, indexes
from functools import reduce


class DataHandler:
    """Data handler for OES spectral data

    This class provides several methods for analysing raw
    spectral data

    DataHandler(xdata, ydata):
    Parameters:
    -----------
        xdata: numpy.array
            pixel on the detector array
        ydata: numpy.array
            Intensity
        cwl: float
            Central Wavelength
        grat: int
            used grating
     """

    def __init__(self, xData, yData, cwl, grat, debug=True, csvoutput=False):
        print("__init__")
        self.debug = debug
        self.xData = xData
        self.yData = yData
        self.cWL = cwl
        # TODO: MAGIC NUMBER, what is 14?
        self.dispersion = 14/grat
        self.process_data()

        if self.debug:
            from logging import basicConfig, getLogger, INFO
            from time import localtime, strftime
            basicConfig(filename='debug.log', level=INFO)
            self.log = getLogger('DataHandler')
            self.log.info(strftime("Start Logging %d.%m.%y %H:%M:%S:",
                                   localtime()))
            
            # TODO: Always except...
#            try:
#                print("Try: setData")
#                self.setData()
#
#            except Exception:
#                print("Except: setData")
#                self.log.exception('Error in DataHandler():')
        else:
            # TODO: setData() is not defined 
            # AND self.debug is always true unless otherwise specified in initialisation( which is never done yet)
            self.log = None
            print("setData")
            self.setData()

        # TODO: csvoutput is always false?
        # AND has no attribute Config
        # AND it would just overwrite self.csvoutput
        if csvoutput:
            csvfile = self.Config.get('CSVOutput', 'Filename')
            self.csvoutput(csvfile)

    def process_data(self):
        """Processes the raw data to obtain the OES spectrum:
            - Sets x values to wavelength
            - Determines baseline and subtracts it
            - Normalizes intensity to baseline intensity
        """

        # Set x values to correct wavelength
        self.procX = self.assign_wavelength(self.xData, self.cWL,
                                            self.dispersion)

        # Assymetic baseline fitting
        # self.procY = self.baseline_als(self.yData, 0.05, 10000)

        # Baseline fitting with peakutils
        self.baseline = baseline(self.yData)
        self.avgbase = reduce(lambda x, y: x + y,
                              self.baseline) / len(self.baseline)
        self.procY = self.yData - self.baseline

        # Normalizing data to average baseline Intensity
        self.procY = self.procY / self.avgbase

        # Find Peak and obtain height and area
        # check: If there are only self.attribute assignments and the 
        # function does not return anything else somewhere, the assignments can
        # be done within the function!
        # check: MAGIC NUMBER
        self.peak_height, self.peak_area, self.peak_position =\
            self.peak_fitting(self.procX, self.procY, 433.5)

    def assign_wavelength(self, xData, cWL, disp):
        """Assigns wavelength to the recorded Pixels """

        center = len(xData)/2
        start = cWL - center*disp
        # convert the data from pixels to wavelength and shift it.
        xData = xData*disp + start
        #check: return xData*disp + (cWL - center*disp)
        return xData

    def peak_fitting(self, xData, yData, wl):
        """Fit peak at wavelength wl """

        # check: MAGIC NUMBER
        i_p = indexes(yData, thres=0.01, min_dist=2)
        peaks = xData[i_p]
        peak_idx = np.where(xData == peaks[(np.abs(xData[i_p] - wl)).argmin()])
        peak_x = float(xData[peak_idx[0]])
        peak_y = float(yData[peak_idx[0]])

        # check: MAGIC NUMBER
        peak_r_border = np.where(
                xData == xData[(np.abs(xData - peak_x-0.1)).argmin()])
        peak_l_border = np.where(
                xData == xData[(np.abs(xData - peak_x+0.2)).argmin()])

        peak_area_x = xData[int(peak_l_border[0]):int(peak_r_border[0])]
        peak_area_y = yData[int(peak_l_border[0]):int(peak_r_border[0])]

        peak_area = np.trapz(peak_area_y, peak_area_x)

        if not wl-1 < peak_x < wl+1:
            # Peak not found
            peak_x = 0
            peak_y = 0
            peak_area = 0

        return peak_y, peak_area, peak_x

    def baseline_als(self, y, lam, p, niter=10):
        """Asymmetric baseline fitting
            Generally 0.001 ≤ p ≤ 0.1 is a good choice
            (for a signal with positive peaks) and 10^2 ≤ λ ≤ 10^9
        """
        L = len(y)
        D = sparse.csc_matrix(np.diff(np.eye(L), 2))
        w = np.ones(L)
        for i in range(niter):
            W = sparse.spdiags(w, 0, L, L)
            Z = W + lam * D.dot(D.transpose())
            z = spsolve(Z, w*y)
            w = p * (y > z) + (1-p) * (y < z)

        return z

    def get_processed_data(self):
        """Returns processed data """
        return self.procX, self.procY

    def get_baseline(self):
        """Returns processed data """
        return self.baseline, self.avgbase

    def get_peak(self):
        """Returns peak data """
        return self.peak_height, self.peak_area

    def get_peak_raw(self):
        """Returns raw peak height and fitting position """
        return self.yData[np.where(self.procX == self.peak_position)],\
            self.peak_position
