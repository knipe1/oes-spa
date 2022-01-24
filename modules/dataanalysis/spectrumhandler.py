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
from .calibration import Calibration
from .fitting import Fitting
from ..filehandling.filereading.filereader import FileReader
from c_types.basicsetting import BasicSetting

# enums
from c_types.integration import Integration
from c_types.peak import Peak
from c_enum.characteristic import CHARACTERISTIC as CHC
from c_enum.error_code import ERROR_CODE as ERR
from c_enum.export_type import EXPORT_TYPE

# exceptions
from exception.CalibrationError import CalibrationError
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
    pixelDataTriggered = pyqtSignal(bool)

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
        result[CHC.REF_AREA] = self._refArea
        result[CHC.REF_HEIGHT] = self._refHeight
        result[CHC.REF_POSITION] = self.refPosition
        result[CHC.CALIBRATION_SHIFT] = self._calibrationShift
        result[CHC.CALIBRATION_PEAKS] = self._calibrationPeaks
        result[CHC.FITTING_FILE] = self._fitting_file
        return result


    ### __methods__

    def __init__(self, file:FileReader, basicSetting:BasicSetting, slotPixel=None, useFileWavelength:bool=False):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)

        if not file.is_valid_spectrum():
            raise InvalidSpectrumError("File contains no valid spectrum.")

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
            self.pixelDataTriggered.connect(slotPixel)

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
        self._refArea = None
        self._refHeight = None
        self.refPosition = None
        self._characteristicValue = None
        self._calibrationShift = None
        self._calibrationPeaks = None


    def fit_data(self, fitting:Fitting)->ERR:
        # Find Peak and obtain height, area, and position
        self.fitting = fitting

        # In case no fitting is selected, the spectrum cannot be displayed.
        try:
            self._fitting_file = fitting.filename
        except AttributeError:
            return ERR.OK

        if fitting is None or fitting.peak is None:
            return ERR.OK

        self._reset_values()

        peak = fitting.peak
        self._peakName = peak.name

        calibrationFile = self.fitting.calibration
        if self.basicSetting.calibration and calibrationFile:
            calibration = Calibration(calibrationFile)
            self._calibrationPeaks = calibration.calibrationPeaks
            try:
                self.procXData, self._calibrationShift = calibration.calibrate(*self.procData.T)
            except CalibrationError as e:
                # TODO: Handle Calibration Error here! See #172
                print(f"Spectrumhandler, line 193 (TODO): {e}")

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
            # Reference
            refCharacteristics, _ = self._analyse_peak(peak.reference)
            self._refHeight = refCharacteristics[CHC.PEAK_HEIGHT]
            self._refArea = refCharacteristics[CHC.PEAK_AREA]
            self.refPosition = refCharacteristics[CHC.PEAK_POSITION]

            characteristicValue, intAreas = self._calculate_characteristic_value(peak)
            self._characteristicValue = characteristicValue
            self.integration.extend(intAreas)

        return ERR.OK


    def _calculate_characteristic_value(self, peak:Peak)->tuple:

        # Default =None. No peak found: =0.0.
        characteristicValue = None
        intAreas = []

        refCharacteristic, refIntegrationAreas = self._analyse_peak(peak.reference)
        refHeight = refCharacteristic[CHC.PEAK_HEIGHT]
        refArea = refCharacteristic[CHC.PEAK_AREA]

        # Set the type for these integration areas.
        integrationAreas = set_type_to_reference(refIntegrationAreas)
        intAreas = integrationAreas.values()

        # Validation
        highRefPeak = (refHeight >= peak.reference.minimumHeight)
        posPeakArea = (self._peakArea > 0)
        posRefPeakArea = (refArea >= 0)
        if highRefPeak and posPeakArea and posRefPeakArea:
            ratio = np.abs(self._peakArea) / np.abs(refArea)
            characteristicValue = np.power(ratio, 2) * peak.normalizationFactorSquared + ratio * peak.normalizationFactor - peak.normalizationOffset
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
        """Assigns wavelength to the recorded Pixels."""

        # Center of the xData. Used for shifting the data.
        rawXData = self.rawXData
        center = uni.get_center(rawXData)

        centralWavelength = self.basicSetting.wavelength
        dispersion = self.basicSetting.dispersion
        xDataArePixel = uni.data_are_pixel(rawXData)
        self.pixelDataTriggered.emit(xDataArePixel)
        if xDataArePixel:
            try:
                # Employs the dispersion to convert pixel to wavelength
                start = centralWavelength - center*dispersion
                shiftedData = rawXData*dispersion + start
            except TypeError:
                self._logger.info("Could not process data. Invalid wavelength or dispersion!")
                shiftedData = rawXData
        else:
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
        invert = -1 if self.basicSetting.invertSpectrum else 1

        rawYData = self.rawYData[::invert]
        # Baseline correction without DC drift.
        # HINT: Issue 121 -> to be reviewed
        meanIntensity = np.mean(rawYData)
        baseline = pkus.baseline(rawYData - meanIntensity) + meanIntensity
        avgbase = np.mean(baseline)

        # Shifting y data and normalization to average baseline intensity.
        # Branchless programming: The baseline is subtracted iff the baselineCorrection is True, but the Interpreter may
        # preload the next line, because we avoid branching here (if statement).
        shiftedYdata = rawYData - baseline * int(self.basicSetting.baselineCorrection)

        normalizeData = self.basicSetting.normalizeData
        if normalizeData:
            processedYdata = shiftedYdata / abs(avgbase)
        else:
            processedYdata = shiftedYdata

        return processedYdata, baseline[::invert], avgbase


def set_type_to_reference(intAreas:dict)->dict:
    for intArea in intAreas.values():
        intArea.peakType = CHC.TYPE_REFERENCE
    return intAreas


def tuple_to_array(data:tuple)->np.ndarray:
    return np.array(data).transpose()