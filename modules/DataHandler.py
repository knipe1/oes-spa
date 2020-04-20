#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data processing module

Contains routines to convert raw data and obtain different parameters

@author: Peter Knittel, Hauke Wernecke
"""

# standard libs
import numpy as np

# third-party libs
from PyQt5.QtCore import QObject, pyqtSignal
from peakutils import baseline, indexes

# local modules/libs
from Logger import Logger
from custom_types.UI_RESULTS import UI_RESULTS


class DataHandler(QObject):
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

    # set up the logger
    logger = Logger(__name__)

    # properties
    _peak_height = 0;
    _peak_area = 0;
    _baseline = 0;

    # qt-signals
    signal_peakHeight = pyqtSignal(str)
    signal_peakArea = pyqtSignal(str)
    signal_peakBaseline = pyqtSignal(str)

    ### Properties - Getter & Setter
    @property
    def peak_height(self) -> float:
        """peak_height getter"""
        return self._peak_height

    @peak_height.setter
    def peak_height(self, height:float):
        """peak_height setter"""
        self._peak_height = height
        self.signal_peakHeight.emit(str(self.peak_height))

    @property
    def peak_area(self) -> float:
        """peak_area getter"""
        return self._peak_area

    @peak_area.setter
    def peak_area(self, area:float):
        """peak_area setter"""
        self._peak_area = area
        self.signal_peakArea.emit(str(self.peak_area))

    @property
    def avgbase(self) -> float:
        """avgbase getter"""
        return self._avgbase

    @avgbase.setter
    def avgbase(self, base:float):
        """avgbase setter"""
        self._avgbase = base
        self.signal_peakBaseline.emit(str(self.avgbase))



    def __init__(self, xData, yData, cWL, grat, funConnection):
        super(DataHandler, self).__init__()
        # TODO: properties to ensure the correct type?
        self.xData = xData
        self.yData = yData
        self.cWL = cWL
        # TODO: MAGIC NUMBER, what is 14?
        self.dispersion = 14/grat

        if funConnection:
            self.InitSignals()
            funConnection(self.signals)

        self.__post_init__()

    def __post_init__(self):
        self.process_data()

    def InitSignals(self):
        self.signals = {UI_RESULTS["tout_PEAK_HEIGHT"]: self.signal_peakHeight,
                        UI_RESULTS["tout_PEAK_AREA"]: self.signal_peakArea,
                        UI_RESULTS["tout_BASELINE"]: self.signal_peakBaseline,
                        }

    def process_data(self):
        """Processes the raw data to obtain the OES spectrum:
            - Sets x values to wavelength.
            - Determines baseline and subtracts it.
            - Normalizes intensity to baseline intensity.
        """

        # Set x values to correct wavelength
        self.procX = self.assign_wavelength(self.xData, self.cWL,
                                            self.dispersion)

        # Baseline fitting with peakutils
        # TODO: what is calculated here?
        # docs: https://peakutils.readthedocs.io/en/latest/reference.html
        self.baseline = baseline(self.yData)
        self.avgbase = np.mean(self.baseline)

        # shifting ydata
        self.procY = self.yData - self.baseline
        # Normalizing data to average baseline Intensity
        # TODO: Check Eichfaktor
        self.procY = self.procY / self.avgbase

        # Find Peak and obtain height and area
        # check: 433.5 is more or less the wavelength of the boron peak
        # TODO: from boron_fitting.conf?
        self.peak_height, self.peak_area, self.peak_position =\
            self.peak_fitting(self.procX, self.procY, 433.5)

    def assign_wavelength(self, xData, cWL, dispersion):
        """Assigns wavelength to the recorded Pixels """

        center = len(xData)/2
        start = cWL - center*dispersion
        # convert the data from pixels to wavelength and shift it.
        xData = xData*dispersion + start
        # TODO: return xData*disp + (cWL - center*disp)
        return xData

    def peak_fitting(self, xData, yData, wl):
        """Fit peak at wavelength wl """

        # TODO: MAGIC NUMBER. From Fitting.
        # Get the indexes of the peaks from the data.
        # Function with rough approximation.
        i_p = indexes(yData, thres=0.01, min_dist=2)

        # getting the index of the peak which is closest to the wavelength
        peak_idx = i_p[np.abs(xData[i_p]-wl).argmin()]
        peak_x = xData[peak_idx]
        peak_y = yData[peak_idx]

        # check: MAGIC NUMBER
        # TODO: from boron_fitting.conf?
        idxBorderRight = np.abs(xData - peak_x-0.1).argmin()
        idxBorderLeft = np.abs(xData - peak_x+0.2).argmin()

        # getting all wavelength(x) and the intensities(y)
        peak_area_x = xData[idxBorderLeft:idxBorderRight]
        peak_area_y = yData[idxBorderLeft:idxBorderRight]

        # Integrate along the given axis using the composite trapezoidal rule.
        peak_area = np.trapz(peak_area_y, peak_area_x)

        # Peak not found
        if not wl-1 < peak_x < wl+1:
            peak_x = 0
            peak_y = 0
            peak_area = 0

        return peak_y, peak_area, peak_x

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
