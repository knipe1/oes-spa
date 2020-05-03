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
from ConfigLoader import ConfigLoader
from Logger import Logger
from custom_types.UI_RESULTS import UI_RESULTS


class DataHandler(QObject):
    """Data handler for OES spectral data

    This class provides several methods for analysing raw spectral data. And
    calculates characteristic values using fittings.

    DataHandler(xdata, ydata):
    Parameters:
    -----------
        xdata: numpy.array
            pixel on the detector array
        ydata: numpy.array
            Intensity
        cwl: float
            Central Wavelength
        grating: int
            used grating
     """

    # set up the logger
    logger = Logger(__name__)

    # properties
    _peakHeight = 0;
    _peakArea = 0;
    _baseline = 0;
    _characteristicValue = 0;

    # qt-signals
    SIG_peakHeight = pyqtSignal(str)
    SIG_peakArea = pyqtSignal(str)
    SIG_peakBaseline = pyqtSignal(str)
    SIG_characteristicValue = pyqtSignal(str)
    SIG_characteristicName = pyqtSignal(str)

    ### Properties - Getter & Setter
    @property
    def peakHeight(self) -> float:
        """peakHeight getter"""
        return self._peakHeight

    @peakHeight.setter
    def peakHeight(self, height:float):
        """peakHeight setter"""
        self._peakHeight = height
        self.SIG_peakHeight.emit(str(self.peakHeight))

    @property
    def peakArea(self) -> float:
        """peakArea getter"""
        return self._peakArea

    @peakArea.setter
    def peakArea(self, area:float):
        """peakArea setter"""
        self._peakArea = area
        self.SIG_peakArea.emit(str(self.peakArea))

    @property
    def avgbase(self) -> float:
        """avgbase getter"""
        return self._avgbase

    @avgbase.setter
    def avgbase(self, base:float):
        """avgbase setter"""
        self._avgbase = base
        self.SIG_peakBaseline.emit(str(self.avgbase))

    @property
    def characteristicValue(self) -> float:
        """avgbase getter"""
        return self._characteristicValue

    @characteristicValue.setter
    def characteristicValue(self, value:float):
        """avgbase setter"""
        self._characteristicValue = value
        self.SIG_characteristicValue.emit(str(self.characteristicValue))
        self.SIG_characteristicName.emit(self.fittings.currentPeak.name)


    def __init__(self, xData, yData, cWL, grating, fittings,
                 funConnection=None):
        super(DataHandler, self).__init__()
        # TODO: properties to ensure the correct type?
        self.xData = xData
        self.yData = yData
        self.cWL = cWL
        # TODO: MAGIC NUMBER, what is 14?
        self.dispersion = 14/grating
        self.fittings = fittings

        if funConnection:
            self.InitSignals()
            funConnection(self.signals)

        self.__post_init__()

    def __post_init__(self):
        self.process_data()


    def InitSignals(self):
        self.signals = {UI_RESULTS.tout_PEAK_HEIGHT: self.SIG_peakHeight,
                        UI_RESULTS.tout_PEAK_AREA: self.SIG_peakArea,
                        UI_RESULTS.tout_BASELINE: self.SIG_peakBaseline,
                        UI_RESULTS.tout_CHARACTERISTIC_VALUE:
                            self.SIG_characteristicValue,
                        UI_RESULTS.tout_BASELINE: self.SIG_peakBaseline,
                        UI_RESULTS.lbl_CHARACTERISTIC_VALUE:
                            self.SIG_characteristicName,
                        }

    def process_data(self):
        """Processes the raw data to obtain the OES spectrum:
            - Sets x values to wavelength.
            - Determines baseline and subtracts it.
            - Normalizes intensity to baseline intensity.
        """

        # Convert x data into wavelengths.
        self.procX = self.assign_wavelength(self.xData, self.cWL,
                                            self.dispersion)

        # Baseline fitting with peakutils
        # TODO: what is calculated here? @knittel/@reinke
        # docs: https://peakutils.readthedocs.io/en/latest/reference.html
        self.baseline = baseline(self.yData)
        self.avgbase = np.mean(self.baseline)

        # shifting y data and normalization to average baseline intensity
        self.procY = self.yData - self.baseline
        self.procY = self.procY / self.avgbase

        # Find Peak and obtain height, area, and position
        self.peakHeight, self.peakArea, self.peakPosition =\
            self.peak_fitting(self.procX, self.procY, 433.5)
        # TODO: Evaluate!
        self.characteristicValue = self.calculate_characteristic_value(
            self.fittings.currentPeak, self.fittings.currentReference)

    def calculate_characteristic_value(self, peak, reference):
        # Calculate characteristics of the peak
        self.peakHeight, self.peakArea, self.peakPosition =\
            self.CalculatePeak(peak, self.procX, self.procY)

        # Calculate characteristics of the reference peak
        refHeight, refArea, refPosition = self.CalculatePeak(reference,
                                                             self.procX,
                                                             self.procY)

        characteristicValue = 0
        if refHeight:
           characteristicValue = self.peakArea / refHeight \
               * self.fittings.currentPeak.normalizationFactor
        print(characteristicValue)
        return characteristicValue


    def assign_wavelength(self, xData, cWL, dispersion):
        """Assigns wavelength to the recorded Pixels """

        center = len(xData)/2
        start = cWL - center*dispersion
        # Convert the data from pixels to wavelength and shift it.
        xData = xData*dispersion + start

        return xData

    def peak_fitting(self, xData:list, yData:list, wl:float)->(float, float,
                                                               float):
        """
        Peak fit at given wavelength.

        Searching the given data for peaks and find the closest peak to the
        wavelength (just closest, due to discrete values). Integrates the peak.

        Parameters
        ----------
        xData : list
            Contains the wavelengths of the spectra.
        yData : list
            Contains the intensities of the spectra.
        wl : float
            The central wavelength of the peak.

        Returns
        -------
        (yPeak:float, peakArea:float, xPeak:float)
            yPeak: The intensity of the peak, aka peak height.
            peakArea: The area of the peak.
            xPeak: The wavelength of the peak.

        """
        THRESHOLD = 0.01
        MIN_DISTANCE = 2

        # TODO: MAGIC NUMBER. From Fitting.
        # Get the indexes of the peaks from the data.
        # Function with rough approximation.
        i_p = indexes(yData, thres=THRESHOLD, min_dist=MIN_DISTANCE)

        # getting the index of the peak which is closest to the wavelength
        idxPeak = i_p[np.abs(xData[i_p]-wl).argmin()]
        xPeak = xData[idxPeak]
        yPeak = yData[idxPeak]
        self.rawPeak = (xPeak, self.yData[idxPeak])

        # check: MAGIC NUMBER
        # TODO: from boron_fitting.conf?
        idxBorderRight = np.abs(xData - xPeak-0.1).argmin()
        idxBorderLeft = np.abs(xData - xPeak+0.2).argmin()

        # getting all wavelength(x) and the intensities(y)
        peakAreaX = xData[idxBorderLeft:idxBorderRight]
        peakAreaY = yData[idxBorderLeft:idxBorderRight]

        # Integrate along the given axis using the composite trapezoidal rule.
        peakArea = np.trapz(peakAreaY, peakAreaX)

        # Peak not found
        if not wl-1 < xPeak < wl+1:
            xPeak = 0
            yPeak = 0
            peakArea = 0

        return yPeak, peakArea, xPeak

    ### prototype
    def CalculatePeak(self, peak, procXData:list, procYData:list)->(float,
                                                                    float,
                                                                    float):
        """
        Peak fit at given wavelength.

        Searching the given data for peaks and find the closest peak to the
        wavelength (just closest, due to discrete values). Integrates the peak.

        Parameters
        ----------
        peak : Peak
            Defines the values for the analysis of the peak.
        procXData : list
            Contains the wavelengths of the spectra.
        procYData : list
            Contains the intensities of the spectra.

        Returns
        -------
        (yPeak:float, peakArea:float, xPeak:float)
            yPeak: The intensity of the peak, aka peak height.
            peakArea: The area of the peak.
            xPeak: The wavelength of the peak.

        """
        THRESHOLD = 0.01
        MIN_DISTANCE = 2

        # Get the indexes of the peaks from the data.
        # Function with rough approximation.
        idxPeaksApprox = indexes(procYData, thres=THRESHOLD,
                                 min_dist=MIN_DISTANCE)

        # getting the index of the peak which is closest to the wavelength
        diffWavelength = np.abs(procXData[idxPeaksApprox]-peak.centralWavelength)
        idxPeak = idxPeaksApprox[diffWavelength.argmin()]
        xPeak = procXData[idxPeak]
        yPeak = procYData[idxPeak]
        self.rawPeak = (xPeak, self.yData[idxPeak])

        # get the borders for integration
        idxBorderRight = np.abs(procXData - peak.upperLimit).argmin()
        idxBorderLeft = np.abs(procXData - peak.lowerLimit).argmin()


        # getting all wavelength(x) and the intensities(y)
        peakAreaX = procXData[idxBorderLeft:idxBorderRight]
        peakAreaY = procYData[idxBorderLeft:idxBorderRight]

        # Integrate along the given axis using the composite trapezoidal rule.
        peakArea = np.trapz(peakAreaY, peakAreaX)


        # validation
        if yPeak <= peak.minimum:
            return 0, 0, 0
        # TODO: further validation?!?

        return yPeak, peakArea, xPeak


    def get_processed_data(self):
        """Returns processed data """
        return self.procX, self.procY

    def get_baseline(self):
        """Returns processed data """
        return self.baseline, self.avgbase

    def get_peak(self):
        """Returns peak data """
        return self.peakHeight, self.peakArea

    def get_raw_peak(self):
        """Returns raw  fitting position and peak intensity"""
        return self.rawPeak
