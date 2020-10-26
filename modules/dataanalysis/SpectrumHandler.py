#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data processing module

Contains routines to convert raw data and obtain different parameters

Glossary:
    rawData: the data that is originally in the spectrum file.
    procData: 'processed' data-> the raw data somwhow processed like converting from pixel to wavelength or shift it to some wavelength.

@author: Peter Knittel, Hauke Wernecke
"""

# standard libs
import numpy as np

# third-party libs
import peakutils as pkus

# local modules/libs
from Logger import Logger
import modules.Universal as uni
from modules.filehandling.filereading.FileReader import FileReader
from custom_types.BasicSetting import BasicSetting

# enums
from custom_types.Integration import Integration
from custom_types.Peak import Peak
from custom_types.ASC_PARAMETER import ASC_PARAMETER as ASC
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC
from custom_types.ERROR_CODE import ERROR_CODE as ERR
from custom_types.EXPORT_TYPE import EXPORT_TYPE


class SpectrumHandler():
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

    ### Properties

    @property
    def rawData(self)->np.ndarray:
        return self._rawData

    @rawData.setter
    def rawData(self, xyData:tuple)->None:
        self._rawData = tuple_to_array(xyData)


    @property
    def procData(self)->np.ndarray:
        return self._processedData

    @procData.setter
    def procData(self, xyData:tuple)->None:
        self._processedData = tuple_to_array(xyData)

    @property
    def procXData(self)->np.ndarray:
        return self.procData[:, 0]

    @property
    def procYData(self)->np.ndarray:
        return self.procData[:, 1]


    ### dunder methods

    def __init__(self, basicSetting, **kwargs):
        # Set up the logger.
        self.logger = Logger(__name__)

        parameter = kwargs.get("parameter", {})
        self.basicSetting = basicSetting

        self.dispersion = self.determine_dispersion(parameter)


    def __repr__(self):
        info = {}
        info["Peak Height"] = self.peakHeight
        info["Peak Area"] = self.peakArea
        info["Peak Position"] = self.peakPosition
        info["Baseline"] = self.avgbase
        info["Characteristic"] = self.characteristicValue
        return self.__module__ + ":\n" + str(info)


    def analyse_data(self, file:FileReader)->ERR:
        # Get raw data. Process data and calculate characteristic values.
        errorcode = file.is_valid_spectrum()
        if not errorcode:
            self.logger.warning("Could not analyse spectrum.")
            return errorcode

        self.rawData = file.data
        self.procData, self.baseline, self.avgbase = process_data(self.rawData, self.basicSetting, self.dispersion)

        # Find Peak and obtain height, area, and position
        peak = self.basicSetting.fitting.peak

        peakCharacteristics, integrationAreas = self.analyse_peak(peak)
        self.peakHeight = peakCharacteristics[CHC.PEAK_HEIGHT]
        self.peakArea = peakCharacteristics[CHC.PEAK_AREA]
        self.peakPosition = peakCharacteristics[CHC.PEAK_POSITION]
        self.integration = list(integrationAreas.values())

        characteristicValue, intAreas = self.calculate_characteristic_value(peak)
        self.characteristicValue = characteristicValue
        self.integration.extend(intAreas)

        return ERR.OK


    def calculate_characteristic_value(self, peak:Peak)->tuple:

        # Default is None to distuinguish issues during the analysis and just no peak (=0).
        characteristicValue = None
        intAreas = []

        if not hasattr(peak, "reference"):
            return characteristicValue, intAreas

        peakCharacteristics, _ = self.analyse_peak(peak)
        peakArea = peakCharacteristics[CHC.PEAK_AREA]

        refCharacteristic, refIntegrationAreas = self.analyse_peak(peak.reference)
        refHeight = refCharacteristic[CHC.PEAK_HEIGHT]
        refArea = refCharacteristic[CHC.PEAK_AREA]

        # Set the type for these integration areas.
        integrationAreas = self.set_type_to_reference(refIntegrationAreas)
        intAreas = integrationAreas.values()

        # Validation
        if refHeight >= peak.reference.minimum:
            ratio = peakArea / refArea
            characteristicValue = ratio * peak.normalizationFactor - peak.normalizationOffset
        else:
            characteristicValue = 0.0

        return characteristicValue, intAreas


    def analyse_peak(self, peak:Peak)->(dict, dict):
        """

        Searching the given data for peaks and find the closest peak to the
        wavelength (just closest, due to discrete values). Integrates the peak.

        Parameters
        ----------
        peak : Peak
            Defines the values for the analysis of the peak.

        """
        integrationRange = self.get_integration_range(peak)
        xPeak, yPeak, peakArea = self.get_peak_characteristics(integrationRange)

        characteristics = {CHC.PEAK_POSITION: xPeak,
                           CHC.PEAK_HEIGHT: yPeak,
                           CHC.PEAK_AREA: peakArea,}

        # Determine integration areas.
        integrationRaw = Integration(self.rawData[integrationRange])
        integrationProcessed = Integration(self.procData[integrationRange], spectrumType=EXPORT_TYPE.PROCESSED)
        integrationAreas = {CHC.INTEGRATION_RAW: integrationRaw,
                            CHC.INTEGRATION_PROCESSED: integrationProcessed}

        return characteristics, integrationAreas


    def get_integration_range(self, peak:Peak)->range:
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


    def get_peak_characteristics(self, integrationRange:range):

        procXData, procYData = self.procXData, self.procYData

        # Get the highest Peak in the integration area.
        try:
            idxPeak = procYData[integrationRange].argmax() + integrationRange[0]
        except ValueError:
            return 0.0, 0.0, 0.0

        xPeak = procXData[idxPeak]
        yPeak = procYData[idxPeak]

        # getting all wavelength(x) and the intensities(y)
        peakAreaX = procXData[integrationRange]
        peakAreaY = procYData[integrationRange]
        # Integrate along the given axis using the composite trapezoidal rule.
        peakArea = np.trapz(peakAreaY, peakAreaX)

        return xPeak, yPeak, peakArea


    def get_integration_areas(self):
        rawIntegration = []
        procIntegration = []
        for intArea in self.integration:
            if intArea.spectrumType == EXPORT_TYPE.RAW:
                rawIntegration.append(intArea)
            elif intArea.spectrumType == EXPORT_TYPE.PROCESSED:
                procIntegration.append(intArea)

        return rawIntegration, procIntegration


    def set_type_to_reference(self, intAreas:dict)->dict:
        for intArea in intAreas.values():
            intArea.peakType = CHC.TYPE_REFERENCE
        return intAreas


    def determine_dispersion(self, parameter:dict)->float:
        # see #51 on git
        try:
            # 12.04391 -> delta wl
            dispersion = 12.04391 / parameter[ASC.GRAT]
        except KeyError:
            # 12.042204 -> analysed with asc-data
            dispersion = 12.042204 / self.basicSetting.grating
        return dispersion


    def has_valid_peak(self):
        try:
            return (self.peakHeight != 0.0)
        except AttributeError:
            return False


def process_data(rawData:np.ndarray, setting:BasicSetting, dispersion:float):
    """Processes the raw data with regard to the given wavelength and the dispersion."""
    procXData = process_x_data(rawData[:, 0], setting.wavelength, dispersion)
    procYData, baseline, avgbase = process_y_data(rawData[:, 1], setting.baselineCorrection)
    return (procXData, procYData), baseline, avgbase


def process_x_data(rawXData:np.ndarray, centralWavelength:float, dispersion:float):
    """Assigns wavelength to the recorded Pixels """

    # Center of the xData. Used for shifting the data.
    center = rawXData[len(rawXData) // 2 - 1]     # offset of python lists.

    xDataArePixel = uni.data_are_pixel(rawXData)
    # The difference is 1 if pixels are recorded. Data with a smaller difference contain wavelength data.
    if xDataArePixel:
        # Employs the dispersion to convert pixel to wavelength
        start = centralWavelength - center*dispersion
        shiftedData = rawXData*dispersion + start
    else:
        # Only shift the original data to the given centralWavelength
        shift = centralWavelength - center
        shiftedData = rawXData + shift

    return shiftedData


def process_y_data(rawYData:np.ndarray, baselineCorrection:bool):
    # Baseline fitting with peakutils.
    # TODO: what is calculated here? @knittel/@reinke
    # Docs: https://peakutils.readthedocs.io/en/latest/reference.html
    baseline = pkus.baseline(rawYData)
    avgbase = np.mean(baseline)

    # Shifting y data and normalization to average baseline intensity.
    if baselineCorrection:
        shiftedYdata = rawYData - baseline
    else:
        shiftedYdata = rawYData
    processedYdata = shiftedYdata / abs(avgbase)
    return processedYdata, baseline, avgbase


def tuple_to_array(data:tuple)->np.ndarray:
    return np.array(data).transpose()