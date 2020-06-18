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
from custom_types.Integration import Integration


class DataHandler(QObject):
    """Data handler for OES spectral data.

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

    # TODO: neccesary?
    # properties
    _peakHeight = 0;
    _peakArea = 0;
    _baseline = 0;
    _characteristicValue = 0;

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
        chcName = self.basicSetting.fitting.currentPeak.name or "No name defined!"
        self.SIG_characteristicName.emit(chcName)



    def __init__(self, basicSetting, **kwargs):
        # TODO: optional update Plots
        # TODO: display graph -> use spectrum here?
        # TODO: export Characteristics

        super(DataHandler, self).__init__()

        # Convert optional str to list to ensure handling with lists.
        # if isinstance(filelist, str):
        #     filelist = [filelist]
        # self.filelist = filelist;

        self.basicSetting = basicSetting
        # TODO: Calculation of dispersion. How to distinguish asc, spk, csv file?
        parameter = kwargs.get("parameter")
        try:
            # 12.04391 -> delta wl
            self.dispersion = 12.04391 / parameter[ASC.GRAT]
        except:
            # 12.042204 -> analysed with asc-data: used instead of 14
            self.dispersion = 12.042204 / basicSetting.grating

        if kwargs.get("funConnection"):
            self.signals = self.init_signals()
            kwargs["funConnection"](self.signals)

    def __post_init__(self):
        self.analyse_data()


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


    @staticmethod
    def assign_wavelength(xData, cWL, dispersion):
        """Assigns wavelength to the recorded Pixels """

        center = xData[len(xData) // 2 - 1] # offset of python lists.
        # TODO: implicit pixels?!
        if  xData[1] - xData[0] == 1:
            start = cWL - center*dispersion
            # Convert the data from pixels to wavelength and shift it.
            shiftedData = xData*dispersion + start
        else:
            shift = cWL - center
            shiftedData = xData + shift

        return shiftedData


    @staticmethod
    def extract_data(file:FileReader):

        # TODO: error handling
        xData, yData = None, None

        # Validation.
        if file.is_valid_datafile():
            # TODO: Why not as tuples? just data = [(x0, y0),(x1, y1),...]
            xData, yData = file.data

        return (xData, yData)


    def process_data(self, xData, yData):

        # Convert x data into wavelengths.
        procXData = self.assign_wavelength(xData, self.basicSetting.wavelength,
                                               self.dispersion)
        # if xData[1] - xData[0] == 1:
        #     procXData = self.assign_wavelength(xData, self.basicSetting.wavelength,
        #                                        self.dispersion)
        # else:
        #     procXData = xData

        # Baseline fitting with peakutils
        # TODO: what is calculated here? @knittel/@reinke
        # docs: https://peakutils.readthedocs.io/en/latest/reference.html
        baseline = pkus.baseline(yData)
        avgbase = np.mean(baseline)

        # shifting y data and normalization to average baseline intensity
        procYData = yData - baseline
        procYData = procYData / avgbase

        return (procXData, procYData), baseline, avgbase


    def analyse_data(self, file:FileReader):
        """Processes the raw data to obtain the OES spectrum:
            - Sets x values to wavelength.
            - Determines baseline and subtracts it.
            - Normalizes intensity to baseline intensity.
        """

        # Get raw data. Process data and calculate characteristic values.
        if not file.is_valid_datafile():
            dialog.critical_unknownFiletype()
            return None

        data = self.extract_data(file)
        self.data = data
        procData, baseline, avgbase = self.process_data(*data)

        fitting = self.basicSetting.fitting

        # Find Peak and obtain height, area, and position
        peakChcs = self.calculate_peak(fitting.currentPeak, *procData)
        # TODO: Evaluate!
        try:
            characteristicValue, intAreas = self.calculate_characteristic_value(
                fitting.currentPeak, fitting.currentReference, *procData)
        except:
            # This is also displayed in the text field.
            # TODO: May be also be exported? Issue?
            characteristicValue = "No reference defined."

        # Assign data to instance.
        self.data = data
        self.procData = procData
        self.baseline = baseline
        self.avgbase = avgbase
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


    def calculate_characteristic_value(self, peak, reference, procX, procY):

        # Default is None to distuinguish issues during the analysis and just
        # no peak.
        characteristicValue = None
        intAreas = []

        # TODO: Doublecheck Area/Height?

        # Calculate characteristics of the peak
        peakChcs = self.calculate_peak(peak, procX, procY)
        peakArea = peakChcs[CHC.PEAK_AREA]
        intAreas.append(peakChcs[CHC.INTEGRATION_PXL])
        intAreas.append(peakChcs[CHC.INTEGRATION_WL])

        # Calculate characteristics of the reference peak
        refChcs = self.calculate_peak(reference, procX, procY)
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


    def calculate_peak(self, peak, procXData:list, procYData:list)->(dict):
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
        if yPeak <= peak.minimum:
            yPeak, xPeak, peakArea = 0, 0, 0
        # TODO: further validation?!?

        results[CHC.PEAK_HEIGHT] = yPeak
        results[CHC.PEAK_POSITION] = xPeak
        results[CHC.PEAK_AREA] = peakArea
        results[CHC.INTEGRATION_PXL] = integrationPlx
        results[CHC.INTEGRATION_WL] = integrationWl

        return results
