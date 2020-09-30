#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data processing module

Contains routines to convert raw data and obtain different parameters

@author: Peter Knittel, Hauke Wernecke
"""

# standard libs
import numpy as np

# third-party libs
import peakutils as pkus

# local modules/libs
from Logger import Logger
import dialog_messages as dialog
from modules.FileReader import FileReader

# enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE
from custom_types.ASC_PARAMETER import ASC_PARAMETER as ASC
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC
from custom_types.ERROR_CODE import ERROR_CODE as ERR
from custom_types.Integration import Integration


class SpectrumHandler():
    """Data handler for OES spectral data.

    This class provides several methods for analysing raw spectral data. And
    calculates characteristic values using fittings.

    SpectrumHandler(basicSetting, **kwargs):
    Parameters:
    -----------
        basicSetting:
            The selected setting. Includes information regarding the analysis.
        **kwargs:
            parameter:
                Information about wavelength, dispersion,...
     """

    ### Properties - Getter & Setter

    @property
    def rawData(self) -> np.ndarray:
        return self._rawData

    @rawData.setter
    def rawData(self, xyData:tuple):
        """Raw x and y data."""
        self._rawData = np.array(xyData).transpose()


    @property
    def procData(self) -> tuple:
        """Processed x and y data."""
        return self._processedData

    @procData.setter
    def procData(self, xyData:tuple):
        """Processed x and y data."""
        self._processedData = np.array(xyData).transpose()


    def __init__(self, basicSetting, **kwargs):
        # Set up the logger.
        self.logger = Logger(__name__)

        self.basicSetting = basicSetting

        # TODO: Calculation of dispersion. How to distinguish asc, spk, csv file?
        parameter = kwargs.get("parameter", {})

        try:
            # 12.04391 -> delta wl
            self.dispersion = 12.04391 / parameter[ASC.GRAT]
        except KeyError:
            # 12.042204 -> analysed with asc-data: used instead of 14
            self.dispersion = 12.042204 / basicSetting.grating

        self.reset_characteristics()


    def __repr__(self):
        info = {}
        info["Peak Height"] = self.peakHeight
        info["Peak Area"] = self.peakArea
        info["Peak Position"] = self.peakPosition
        info["Baseline"] = self.avgbase
        info["Characteristic"] = self.characteristicValue
        return self.__module__ + ":\n" + str(info)


    def reset_characteristics(self):
        self.characteristicValue = 0.0
        self.peakArea = 0.0
        self.peakHeight = 0.0
        self.peakPosition = 0.0


    def analyse_data(self, file:FileReader):
        # Get raw data. Process data and calculate characteristic values.
        errorcode = file.is_valid_spectrum()
        if errorcode != ERR.OK:
            dialog.critical_invalidSpectrum()
            self.logger.warning("Could not analyse spectrum.")
            return errorcode

        self.rawData = file.data
        self.procData, self.baseline, self.avgbase = process_data(self.rawData, self.basicSetting.wavelength, self.dispersion)

        # Find Peak and obtain height, area, and position
        fitting = self.basicSetting.fitting
        self.integration = []
        try:
            peakCharacteristics, integrationAreas = self.calculate_peak(fitting.peak)
            self.peakHeight = peakCharacteristics[CHC.PEAK_HEIGHT]
            self.peakArea = peakCharacteristics[CHC.PEAK_AREA]
            self.peakPosition = peakCharacteristics[CHC.PEAK_POSITION]
        except TypeError:
            self.reset_characteristics()
            self.logger.warning("Could not calculate peak characteristics.")
            return ERR.OK

        self.integration.append(integrationAreas[CHC.INTEGRATION_RAW])
        self.integration.append(integrationAreas[CHC.INTEGRATION_PROCESSED])

        characteristicValue, intAreas = self.calculate_characteristic_value(fitting.peak)
        self.characteristicValue = characteristicValue
        self.integration.extend(intAreas)

        return ERR.OK


    def calculate_characteristic_value(self, peak):

        # Default is None to distuinguish issues during the analysis and just no peak.
        # Only if any kind of validation is implemented below.
        characteristicValue = None
        intAreas = []

        if not hasattr(peak, "reference"):
            characteristicValue = "No reference defined."
            return characteristicValue, intAreas

        # Calculate characteristics of the peak
        try:
            peakCharacteristics, _ = self.calculate_peak(peak)
            peakArea = peakCharacteristics[CHC.PEAK_AREA]
        except TypeError:
            self.logger.warning("Could not calculate peak characteristics.")

        # Calculate characteristics of the reference peak
        try:
            refCharacteristic, integrationAreas = self.calculate_peak(peak.reference)
            refHeight = refCharacteristic[CHC.PEAK_HEIGHT]
        except TypeError:
            refHeight = 0
            self.logger.warning("Could not calculate reference characteristics.")
        # Set the type for these integration areas.
        integrationAreas[CHC.INTEGRATION_RAW].peakType = CHC.TYPE_REFERENCE
        integrationAreas[CHC.INTEGRATION_PROCESSED].peakType = CHC.TYPE_REFERENCE
        intAreas.append(integrationAreas[CHC.INTEGRATION_RAW])
        intAreas.append(integrationAreas[CHC.INTEGRATION_PROCESSED])

        # TODO: @knittel validation?
        if refHeight >= peak.reference.minimum:
            characteristicValue = peakArea / refHeight * peak.normalizationFactor

        return characteristicValue, intAreas


    def calculate_peak(self, peak)->(dict):
        """
        Peak fit at given wavelength.

        Searching the given data for peaks and find the closest peak to the
        wavelength (just closest, due to discrete values). Integrates the peak.

        Parameters
        ----------
        peak : Peak
            Defines the values for the analysis of the peak.

        Returns
        -------
        (xPeak:float, yPeak:float, peakArea:float)
            xPeak: The wavelength of the peak.
            yPeak: The intensity of the peak, aka peak height.
            peakArea: The area of the peak.

        """
        results = {}
        procXData, procYData = self.procData[:, 0], self.procData[:, 1]

        # get the borders for integration
        lowerLimit = peak.centralWavelength - peak.shiftDown
        upperLimit = peak.centralWavelength + peak.shiftUp
        idxBorderRight = np.abs(procXData - upperLimit).argmin()
        idxBorderLeft = np.abs(procXData - lowerLimit).argmin()
        if (idxBorderRight == 0) or (idxBorderLeft == len(procXData)):
            return
        # +1 in integrationRange due to the last value is omitted in python ranges.
        integrationRange = range(idxBorderLeft, idxBorderRight+1)

        # Get the highest Peak in the integration area.
        idxPeak = procYData[integrationRange].argmax() + idxBorderLeft
        xPeak = procXData[idxPeak]
        yPeak = procYData[idxPeak]

        # getting all wavelength(x) and the intensities(y)
        peakAreaX = procXData[integrationRange]
        peakAreaY = procYData[integrationRange]
        # Integrate along the given axis using the composite trapezoidal rule.
        peakArea = np.trapz(peakAreaY, peakAreaX)
        # determine integration areas.
        integrationRaw = Integration(self.rawData[integrationRange])
        integrationProcessed = Integration(self.procData[integrationRange], spectrumType=EXPORT_TYPE.PROCESSED)


        results[CHC.PEAK_HEIGHT] = yPeak
        results[CHC.PEAK_POSITION] = xPeak
        results[CHC.PEAK_AREA] = peakArea

        integrationAreas = {CHC.INTEGRATION_RAW: integrationRaw,
                            CHC.INTEGRATION_PROCESSED: integrationProcessed}

        return results, integrationAreas


    def get_integration_area(self):
        rawIntegration = []
        procIntegration = []
        for intArea in self.integration:
            if intArea.spectrumType == EXPORT_TYPE.RAW:
                rawIntegration.append(intArea)
            elif intArea.spectrumType == EXPORT_TYPE.PROCESSED:
                procIntegration.append(intArea)

        return rawIntegration, procIntegration




def process_data(rawData:np.ndarray, centralWavelength:float, dispersion:float):
    """Processes the raw data with regard to the given wavelength and the dispersion."""
    procXData = process_x_data(rawData[:, 0], centralWavelength, dispersion)
    procYData, baseline, avgbase = process_y_data(rawData[:, 1])
    return (procXData, procYData), baseline, avgbase


def process_x_data(rawXData:np.ndarray, centralWavelength:float, dispersion:float):
    """Assigns wavelength to the recorded Pixels """
    xDataArePixel = (rawXData[1] - rawXData[0] == 1)

    # Center of the xData. Used for shifting the data.
    center = rawXData[len(rawXData) // 2 - 1]     # offset of python lists.


    # TODO: implicit pixels?! @knittel/@reinke
    # The difference is 1 if pixels are recorded. Data with a smaller difference contain wavelength data.
    if xDataArePixel:
        start = centralWavelength - center*dispersion
        shiftedData = rawXData*dispersion + start
    else:
        # Shifts the rawData to the given centralWavelenght
        shift = centralWavelength - center
        shiftedData = rawXData + shift

    return shiftedData


def process_y_data(rawYData:np.ndarray):
    # Baseline fitting with peakutils.
    # TODO: what is calculated here? @knittel/@reinke
    # Docs: https://peakutils.readthedocs.io/en/latest/reference.html
    baseline = pkus.baseline(rawYData)
    avgbase = np.mean(baseline)

    # Shifting y data and normalization to average baseline intensity.
    shiftedYdata = rawYData - baseline
    processedYdata = shiftedYdata / abs(avgbase)
    return processedYdata, baseline, avgbase