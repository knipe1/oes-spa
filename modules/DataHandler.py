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
import peakutils as pkus

# local modules/libs
from Logger import Logger
import dialog_messages as dialog
from modules.FileReader import FileReader

# enums
from custom_types.UI_RESULTS import UI_RESULTS
from custom_types.EXPORT_TYPE import EXPORT_TYPE
from custom_types.ASC_PARAMETER import ASC_PARAMETER as ASC
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC
from custom_types.ERROR_CODE import ERROR_CODE as ERR
from custom_types.Integration import Integration


class DataHandler(QObject):
    """Data handler for OES spectral data.

    This class provides several methods for analysing raw spectral data. And
    calculates characteristic values using fittings.

    DataHandler(basicSetting, **kwargs):
    Parameters:
    -----------
        basicSetting:
            The selected setting. Includes information regarding the analysis.
        **kwargs:
            parameter:
                Information about wavelength, dispersion,... often provided by
                an .asc-file.
            funConnection:
                Function handler to connect qtSignals to ui slots.
     """

    # Qt-signals.
    SIG_peakHeight = pyqtSignal(str)
    SIG_peakArea = pyqtSignal(str)
    SIG_peakBaseline = pyqtSignal(str)
    SIG_characteristicValue = pyqtSignal(str)
    SIG_characteristicName = pyqtSignal(str)

    ### Properties - Getter & Setter

    @property
    def peakHeight(self) -> float:
        """peakHeight getter"""
        return self._peakHeight or 0.0

    @peakHeight.setter
    def peakHeight(self, height:float):
        """peakHeight setter"""
        self._peakHeight = height
        self.SIG_peakHeight.emit(str(self.peakHeight))

    @property
    def peakArea(self) -> float:
        """peakArea getter with def. value"""
        return self._peakArea or 0.0

    @peakArea.setter
    def peakArea(self, area:float):
        """peakArea setter"""
        self._peakArea = area
        self.SIG_peakArea.emit(str(self.peakArea))

    @property
    def avgbase(self) -> float:
        """avgbase getter"""
        return self._avgbase or 0.0

    @avgbase.setter
    def avgbase(self, base:float):
        """avgbase setter"""
        self._avgbase = base
        self.SIG_peakBaseline.emit(str(self.avgbase))

    @property
    def characteristicValue(self) -> float:
        """avgbase getter"""
        return self._characteristicValue or 0.0

    @characteristicValue.setter
    def characteristicValue(self, value:float):
        """avgbase setter"""
        self._characteristicValue = value
        self.SIG_characteristicValue.emit(str(self.characteristicValue))
        chcName = self.basicSetting.fitting.peak.name or "No name defined!"
        self.SIG_characteristicName.emit(chcName)


    @property
    def data(self) -> tuple:
        """Raw x and y data."""
        return self.xData, self.yData

    @data.setter
    def data(self, xyData:tuple):
        """Raw x and y data."""
        self.xData = xyData[0]
        self.yData = xyData[1]


    @property
    def procData(self) -> tuple:
        """Raw x and y processed data."""
        return self.procXData, self.procYData

    @procData.setter
    def procData(self, procXYData:tuple):
        """Raw x and y processed data."""
        self.procXData = procXYData[0]
        self.procYData = procXYData[1]



    def __init__(self, basicSetting, **kwargs):

        super(DataHandler, self).__init__()

        # set up the logger
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
        except TypeError:
            self.logger.error("No valid set of paramter given, not even an empty dict.")

        if kwargs.get("funConnection"):
            self.signals = self.init_signals()
            kwargs["funConnection"](self.signals)


    def __repr__(self):
        info = {}
        info["Peak Height"] = self.peakHeight
        info["Peak Area"] = self.peakArea
        info["Peak Position"] = self.peakPosition
        info["Baseline"] = self.avgbase
        info["Characteristic"] = self.characteristicValue
        return self.__module__ + ":\n" + str(info)


    def init_signals(self):
        mapping = {UI_RESULTS.tout_PEAK_HEIGHT: self.SIG_peakHeight,
                    UI_RESULTS.tout_PEAK_AREA: self.SIG_peakArea,
                    UI_RESULTS.tout_BASELINE: self.SIG_peakBaseline,
                    UI_RESULTS.tout_CHARACTERISTIC_VALUE:
                        self.SIG_characteristicValue,
                    UI_RESULTS.lbl_CHARACTERISTIC_VALUE:
                        self.SIG_characteristicName,
                    }
        return mapping


    def assign_wavelength(self):
        """Assigns wavelength to the recorded Pixels """

        xData = self.xData
        cWL = self.basicSetting.wavelength
        dispersion = self.dispersion

        # Center of the xData. Used for shifting the data.
        center = xData[len(xData) // 2 - 1]     # offset of python lists.

        # TODO: implicit pixels?! @knittel/@reinke
        # The difference is 1 if pixels are recorded. Data with a smaller
        # difference contain wavelength data.
        if  xData[1] - xData[0] == 1:
            # Convert the data from pixels to wavelength. The wl difference
            # between two data points is defined by the dispersion.
            start = cWL - center*dispersion
            shiftedData = xData*dispersion + start
        else:
            # Allows to set a new wl even if defined in file. Or for exported
            # spectra.
            shift = cWL - center
            shiftedData = xData + shift

        return shiftedData


    def process_data(self):
        """
        Convert raw data and assign to wavelength with baseline information.

        Sets self.procData.
        Sets self.baseline.
        Sets self.avgbase.

        Returns
        -------
        None. Assigns the extracted information to instance.

        """
        if not isinstance(self.xData[0], float):
            # TODO: is Batch
            return

        # Convert x data into wavelengths or just shift it.
        procXData = self.assign_wavelength()

        # Baseline fitting with peakutils.
        # TODO: what is calculated here? @knittel/@reinke
        # Docs: https://peakutils.readthedocs.io/en/latest/reference.html
        baseline = pkus.baseline(self.yData)
        avgbase = np.mean(baseline)

        # Shifting y data and normalization to average baseline intensity.
        procYData = self.yData - baseline
        procYData = procYData / avgbase

        self.procData = (procXData, procYData)
        self.baseline = baseline
        self.avgbase = avgbase


    def analyse_data(self, file:FileReader):
        """Processes the raw data to obtain the OES spectrum:
            - Sets x values to wavelength.
            - Determines baseline and subtracts it.
            - Normalizes intensity to baseline intensity.
        """

        # Get raw data. Process data and calculate characteristic values.
        if file.check_datafile() != ERR.OK:
            dialog.critical_unknownFiletype()
            # TODO: log Error
            return None


        self.data = file.data
        self.process_data()

        fitting = self.basicSetting.fitting

        # Find Peak and obtain height, area, and position
        peakChcs = self.calculate_peak(fitting.peak)
        # TODO: Evaluate!
        try:
            characteristicValue, intAreas = self.calculate_characteristic_value(
                fitting.peak, fitting.reference)
        except AttributeError:
            # This is also displayed in the text field.
            # TODO: May be also be exported? Issue?
            characteristicValue = "No reference defined."

        # Assign data to instance.
        self.peakHeight = peakChcs[CHC.PEAK_HEIGHT]
        self.peakArea = peakChcs[CHC.PEAK_AREA]
        self.peakPosition = peakChcs[CHC.PEAK_POSITION]
        self.characteristicValue = characteristicValue

        self.integration = []
        try:
            self.integration.extend(intAreas)
        except UnboundLocalError:
            self.logger.warning("""No characteristic value calculated.
                                Therefore no integration areas found.""")
        self.integration.append(peakChcs[CHC.INTEGRATION_PXL])
        self.integration.append(peakChcs[CHC.INTEGRATION_WL])

        return 0


    def calculate_characteristic_value(self, peak, reference):

        # Default is None to distuinguish issues during the analysis and just
        # no peak.
        characteristicValue = None
        intAreas = []
        procX, procY = self.procData

        # TODO: Doublecheck Area/Height?

        # Calculate characteristics of the peak
        peakChcs = self.calculate_peak(peak)
        peakArea = peakChcs[CHC.PEAK_AREA]
        intAreas.append(peakChcs[CHC.INTEGRATION_PXL])
        intAreas.append(peakChcs[CHC.INTEGRATION_WL])

        # Calculate characteristics of the reference peak
        refChcs = self.calculate_peak(reference)
        refHeight = refChcs[CHC.PEAK_HEIGHT]
        refChcs[CHC.INTEGRATION_PXL].peakType = CHC.TYPE_REFERENCE
        refChcs[CHC.INTEGRATION_WL].peakType = CHC.TYPE_REFERENCE
        intAreas.append(refChcs[CHC.INTEGRATION_PXL])
        intAreas.append(refChcs[CHC.INTEGRATION_WL])

        # TODO: validation?!
        # HINT: refHeight most times has a value unequal 0, therefore is
        # most often true.
        if refHeight:
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
        # THRESHOLD = 0.01
        # MIN_DISTANCE = 2

        results = {}
        procXData, procYData = self.procData

        # # Get the indexes of the peaks from the data.
        # # Function with rough approximation.
        # idxPeaksApprox = pkus.indexes(procYData, thres=THRESHOLD,
        #                          min_dist=MIN_DISTANCE)


        # get the borders for integration
        lowerLimit = peak.centralWavelength - peak.shiftDown
        upperLimit = peak.centralWavelength + peak.shiftUp
        idxBorderRight = np.abs(procXData - upperLimit).argmin()
        idxBorderLeft = np.abs(procXData - lowerLimit).argmin()
        idxInt = range(idxBorderLeft, idxBorderRight+1)

        # Get the highest Peak in the integration area.
        idxPeak = procYData[idxInt].argmax() + idxBorderLeft
        xPeak = procXData[idxPeak]
        yPeak = procYData[idxPeak]


        # getting all wavelength(x) and the intensities(y)
        peakAreaX = procXData[idxInt]
        peakAreaY = procYData[idxInt]
        integrationPlx = Integration(self.data[0][idxInt],
                                     self.data[1][idxInt])

        integrationWl = Integration(peakAreaX, peakAreaY,
                                    spectrumType=EXPORT_TYPE.PROCESSED)

        # Integrate along the given axis using the composite trapezoidal rule.
        peakArea = np.trapz(peakAreaY, peakAreaX)

        # validation
        # if yPeak <= peak.minimum:
            # yPeak, xPeak, peakArea = 0, 0, 0
        # TODO: further validation?!?

        results[CHC.PEAK_HEIGHT] = yPeak
        results[CHC.PEAK_POSITION] = xPeak
        results[CHC.PEAK_AREA] = peakArea
        results[CHC.INTEGRATION_PXL] = integrationPlx
        results[CHC.INTEGRATION_WL] = integrationWl

        return results
