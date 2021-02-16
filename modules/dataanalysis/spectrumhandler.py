#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data processing module

Contains routines to convert raw data and obtain different parameters

Glossary:
    rawData:
        Data origins from the spectrum file.
    procData:
        'processed' data-> the raw data processed like converting from pixel to wavelength or shift it to some wavelength.

@author: Peter Knittel, Hauke Wernecke
"""


# standard libs
import logging
import numpy as np

# third-party libs
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog
import peakutils as pkus

# local modules/libs
import modules.universal as uni
from modules.dataanalysis.Calibration import Calibration
from modules.dataanalysis.Fitting import Fitting
from modules.filehandling.filereading.filereader import FileReader
from c_types.BasicSetting import BasicSetting

# enums
from c_types.Integration import Integration
from c_types.Peak import Peak
from c_enum.CHARACTERISTIC import CHARACTERISTIC as CHC
from c_enum.ERROR_CODE import ERROR_CODE as ERR
from c_enum.EXPORT_TYPE import EXPORT_TYPE

# exceptions
from exception.InvalidSpectrumError import InvalidSpectrumError
from exception.ParameterNotSetError import ParameterNotSetError


class SpectrumHandler(QDialog):
    """Handles and analyses spectra.

    SpectrumHandler(basicSetting, **kwargs):
    Parameters:
    -----------
        basicSetting:
            The selected setting. Includes information regarding the analysis.
        **kwargs:
            parameter:
                Information about wavelength, dispersion,...
     """
    ### Signals
    signal_pixel_data = pyqtSignal(bool)

    ### Properties

    @property
    def rawData(self)->np.ndarray:
        return self._rawData

    @rawData.setter
    def rawData(self, xyData:tuple)->None:
        self._rawData = xyData


    @property
    def rawXData(self)->np.ndarray:
        return self.rawData[:, 0]

    @property
    def rawYData(self)->np.ndarray:
        return self.rawData[:, 1]


    @property
    def procData(self)->np.ndarray:
        return self._processedData

    @procData.setter
    def procData(self, xyData:tuple)->None:
        self._processedData = tuple_to_array(xyData)

    @property
    def procXData(self)->np.ndarray:
        return self.procData[:, 0]

    @procXData.setter
    def procXData(self, xData:np.ndarray)->None:
        self.procData[:, 0] = xData

    @property
    def procYData(self)->np.ndarray:
        return self.procData[:, 1]


    @property
    def results(self)->dict:
        result = {}
        result[CHC.BASELINE] = self._avgbase
        result[CHC.CHARACTERISTIC_VALUE] = self._characteristicValue
        result[CHC.PEAK_NAME] = self._peakName
        result[CHC.PEAK_AREA] = self._peakArea
        result[CHC.PEAK_HEIGHT] = self._peakHeight
        result[CHC.PEAK_POSITION] = self.peakPosition
        result[CHC.CALIBRATION_SHIFT] = self._calibrationShift
        result[CHC.CALIBRATION_PEAKS] = self._calibrationPeaks
        return result


    ### __methods__

    def __init__(self, file:FileReader, basicSetting:BasicSetting, slotPixel=None, useFileWavelength:bool=False):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)

        if not file.is_valid_spectrum():
            raise InvalidSpectrumError("File contain no valid spectrum.")

        if useFileWavelength:
            try:
                basicSetting.wavelength = file.WAVELENGTH
            except ParameterNotSetError:
                pass

        self.basicSetting = basicSetting

        self.integration = []
        self.fitting = None
        self._avgbase = None

        self._reset_values()

        if not slotPixel is None:
            self.signal_pixel_data.connect(slotPixel)

        self.rawData = file.data
        self._process_data()


    def __repr__(self):
        info = {}
        info["Peak Height"] = self._peakHeight
        info["Peak Area"] = self._peakArea
        info["Peak Position"] = self.peakPosition
        info["Baseline"] = self._avgbase
        info["Characteristic"] = self._characteristicValue
        return self.__module__ + ":\n" + str(info)


    def _reset_values(self)->None:
        self._peakArea = None
        self._peakHeight = None
        self._peakName = None
        self.peakPosition = None
        self._characteristicValue = None
        self._calibrationShift = None
        self._calibrationPeaks = None


    def fit_data(self, fitting:Fitting)->ERR:
        # Find Peak and obtain height, area, and position
        self.fitting = fitting
        if fitting is None or fitting.peak is None:
            return ERR.OK

        self._reset_values()

        peak = fitting.peak
        self._peakName = peak.name

        calibrationFile = self.fitting.calibration
        if self.basicSetting.calibration and calibrationFile:
            calibration = Calibration(calibrationFile)
            self._calibrationPeaks = calibration.calibrationPeaks
            self.procXData, self._calibrationShift = calibration.calibrate(*self.procData.T)

        peakCharacteristics, integrationAreas = self._analyse_peak(peak)
        self._peakHeight = peakCharacteristics[CHC.PEAK_HEIGHT]
        self._peakArea = peakCharacteristics[CHC.PEAK_AREA]
        self.peakPosition = peakCharacteristics[CHC.PEAK_POSITION]
        self.integration = list(integrationAreas.values())

        try:
            validReference = peak.has_valid_reference()
        except ValueError:
            validReference = False

        if validReference:
            characteristicValue, intAreas = self._calculate_characteristic_value(peak)
            self._characteristicValue = characteristicValue
            self.integration.extend(intAreas)

        return ERR.OK


    def _calculate_characteristic_value(self, peak:Peak)->tuple:

        # Default =None. No peak found: =0.0.
        characteristicValue = None
        intAreas = []

        peakCharacteristics, _ = self._analyse_peak(peak)
        peakArea = peakCharacteristics[CHC.PEAK_AREA]

        refCharacteristic, refIntegrationAreas = self._analyse_peak(peak.reference)
        refHeight = refCharacteristic[CHC.PEAK_HEIGHT]
        refArea = refCharacteristic[CHC.PEAK_AREA]

        # Set the type for these integration areas.
        integrationAreas = set_type_to_reference(refIntegrationAreas)
        intAreas = integrationAreas.values()

        # Validation
        highRefPeak = (refHeight >= peak.reference.minimumHeight)
        posPeakArea = (peakArea > 0)
        posRefPeakArea = (refArea >= 0)
        if highRefPeak and posPeakArea and posRefPeakArea:
            ratio = np.abs(peakArea) / np.abs(refArea)
            characteristicValue = ratio * peak.normalizationFactor - peak.normalizationOffset
        else:
            characteristicValue = 0.0

        return characteristicValue, intAreas


    def _analyse_peak(self, peak:Peak)->(dict, dict):
        """

        Searching the given data for peaks and find the closest peak to the
        wavelength (just closest, due to discrete values). Integrates the peak.

        Parameters
        ----------
        peak : Peak
            Defines the values for the analysis of the peak.

        """
        integrationRange = self._get_integration_range(peak)
        area, height, position = self._analyze_peak_characteristics(integrationRange)

        characteristics = {CHC.PEAK_POSITION: position,
                           CHC.PEAK_HEIGHT: height,
                           CHC.PEAK_AREA: area,}

        # Determine integration areas.
        integrationRaw = Integration(self.rawData[integrationRange])
        integrationProcessed = Integration(self.procData[integrationRange],
                                           spectrumType=EXPORT_TYPE.PROCESSED)
        integrationAreas = {CHC.INTEGRATION_RAW: integrationRaw,
                            CHC.INTEGRATION_PROCESSED: integrationProcessed}

        return characteristics, integrationAreas


    def _get_integration_range(self, peak:Peak)->range:
        lowerLimit = peak.centralWavelength - peak.shiftDown
        upperLimit = peak.centralWavelength + peak.shiftUp

        xData = self.procXData
        idxBorderRight = np.abs(xData - upperLimit).argmin()
        idxBorderLeft = np.abs(xData - lowerLimit).argmin()

        isBelowSpectrum = (idxBorderRight == 0)
        isAboveSpectrum = (idxBorderLeft == idxBorderRight)
        if isBelowSpectrum or isAboveSpectrum:
            return range(0)

        integrationRange = range(idxBorderLeft, idxBorderRight+1)
        return integrationRange


    def _analyze_peak_characteristics(self, integrationRange:range)->None:

        procXData, procYData = self.procXData, self.procYData

        # Get the highest Peak in the integration area.
        try:
            idxPeak = procYData[integrationRange].argmax() + integrationRange[0]
        except ValueError:
            peakArea = 0.0
            peakHeight = 0.0
            peakPosition = 0.0
            return peakArea, peakHeight, peakPosition

        peakPosition = procXData[idxPeak]
        peakHeight = procYData[idxPeak]

        # getting all wavelength(x) and the intensities(y).
        peakAreaX = procXData[integrationRange]
        peakAreaY = procYData[integrationRange]
        # Integrate along the given axis using the composite trapezoidal rule.
        peakArea = np.trapz(peakAreaY, peakAreaX)
        return peakArea, peakHeight, peakPosition


    def get_integration_areas(self):
        rawIntegration = []
        procIntegration = []
        for intArea in self.integration:
            if intArea.spectrumType == EXPORT_TYPE.RAW:
                rawIntegration.append(intArea)
            elif intArea.spectrumType == EXPORT_TYPE.PROCESSED:
                procIntegration.append(intArea)

        return rawIntegration, procIntegration


    def has_valid_peak(self):
        try:
            return self._peakHeight != 0.0
        except AttributeError:
            return False


    def calibration(self, procXData:np.ndarray, procYData:np.ndarray)->np.ndarray:
        # Retrieve the filename of the fitting
        calibrationFile = self.fitting.calibration
        if calibrationFile is None:
            return procXData

        calibrationPeaks = np.loadtxt(calibrationFile)

        noPeaks = calibrationPeaks.shape[0]

        wlShift = 0.2
        # find indeces of the reference peaks in the proccessed data
        wlIndex = np.zeros((noPeaks), dtype=int)
        maxShift = 0
        for i, wl in enumerate(calibrationPeaks[:, 0]):
            # get the closest index of the processed data
            wlIndex[i] = np.abs(procXData - wl).argmin()
            # determine the range of the convolution
            idxShift = np.abs(procXData - (wl + wlShift)).argmin()
            maxShift = max(idxShift-wlIndex[i], maxShift)

        calibrationIntensities = np.zeros(shape=(noPeaks, 2*maxShift+1))
        for idx in range(-maxShift, maxShift+1):
            for ref in range(noPeaks):
                idxOffset = idx + maxShift
                calibrationIntensities[ref, idxOffset] = procYData[wlIndex[ref] + idx]

        summedIntensities = calibrationIntensities.sum(axis=0)

        shift = summedIntensities.argmax() - (maxShift)
        absShift = (calibrationPeaks[:, 0] - procXData[wlIndex-shift]).mean()

        shiftedData = procXData - absShift
        return shiftedData


    def _process_data(self)->None:
        """Processes the raw data with regard to the given wavelength and the dispersion."""
        procXData = self._process_x_data()
        procYData, self.baseline, self._avgbase = self._process_y_data()
        self.procData = (procXData, procYData)


    def _process_x_data(self)->np.ndarray:
        """Assigns wavelength to the recorded Pixels """

        # Center of the xData. Used for shifting the data.
        rawXData = self.rawXData
        center = get_center(rawXData)

        centralWavelength = self.basicSetting.wavelength
        dispersion = self.basicSetting.dispersion
        xDataArePixel = uni.data_are_pixel(rawXData)
        if xDataArePixel:
            self.signal_pixel_data.emit(True)
            try:
                # Employs the dispersion to convert pixel to wavelength
                start = centralWavelength - center*dispersion
                shiftedData = rawXData*dispersion + start
            except TypeError:
                self._logger.info("Could not process data. Invalid wavelength or dispersion!")
                shiftedData = rawXData
        else:
            self.signal_pixel_data.emit(False)
            try:
                # Only shift the original data to the given centralWavelength
                shift = centralWavelength - center
                shiftedData = rawXData + shift
            except TypeError:
                self._logger.info("Could not process data. Value of wavelength is invalid!")
                shiftedData = rawXData

        return shiftedData


    def _process_y_data(self):
        # Docs: https://peakutils.readthedocs.io/en/latest/reference.html
        rawYData = self.rawYData
        # Baseline correction without DC drift.
        # HINT: Issue 121 -> to be reviewed
        meanIntensity = np.mean(rawYData)
        baseline = pkus.baseline(rawYData - meanIntensity) + meanIntensity
        avgbase = np.mean(baseline)

        # Shifting y data and normalization to average baseline intensity.
        correctBaseline = self.basicSetting.baselineCorrection
        if correctBaseline:
            shiftedYdata = rawYData - baseline
        else:
            shiftedYdata = rawYData

        normalizeData = self.basicSetting.normalizeData
        if normalizeData:
            processedYdata = shiftedYdata / abs(avgbase)
        else:
            processedYdata = shiftedYdata


        return processedYdata, baseline, avgbase


def get_center(data:np.ndarray)->float:
    centerIdx = np.ceil(len(data) / 2 - 1)  # offset of python lists.
    center = data[int(centerIdx)]
    return center


def set_type_to_reference(intAreas:dict)->dict:
    for intArea in intAreas.values():
        intArea.peakType = CHC.TYPE_REFERENCE
    return intAreas


def tuple_to_array(data:tuple)->np.ndarray:
    return np.array(data).transpose()
