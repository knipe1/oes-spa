#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
class: Spectrum

@author: Hauke Wernecke
"""

# standard libs
import logging
import numpy as np

# third-party libs

# local modules/libs
from loader.ConfigLoader import ConfigLoader
from ui.matplotlibwidget import MatplotlibWidget
import modules.Universal as uni


# Enums
from c_types.Integration import Integration
from c_enum.CHARACTERISTIC import CHARACTERISTIC as CHC
from c_enum.EXPORT_TYPE import EXPORT_TYPE


class Spectrum():
    """
    Concatenate properties of a spectrum to join data and plot options.

    Usage:
        from modules.dataanalysis.Spectrum import Spectrum
        spectrum = Spectrum(matplotlibwidget, EXPORT_TYPE)
        spectrum.set_data(data)

    """
    PLOT = ConfigLoader().PLOT

    BASELINE = "baseline"


    @property
    def data(self)->np.ndarray:
        return self._data

    @data.setter
    def data(self, xyData:(tuple, np.ndarray))->None:
        self._data = np.array(xyData)

    @property
    def xData(self)->np.ndarray:
        return self.data[:, 0]

    @classmethod
    def get_labels(cls, exportType:EXPORT_TYPE)->dict:
        """Get the labels according to the export type."""
        if exportType == EXPORT_TYPE.RAW:
            xLabel = cls.PLOT["RAW_X_LABEL"]
            yLabel = cls.PLOT["RAW_Y_LABEL"]
        elif exportType == EXPORT_TYPE.PROCESSED:
            xLabel = cls.PLOT["PROCESSED_X_LABEL"]
            yLabel = cls.PLOT["PROCESSED_Y_LABEL"]
        elif exportType == EXPORT_TYPE.BATCH:
            xLabel = cls.PLOT["BATCH_X_LABEL"]
            yLabel = cls.PLOT["BATCH_Y_LABEL"]
        labels = {"xLabel": xLabel, "yLabel": yLabel}
        return labels


    @classmethod
    def get_markup(cls, exportType:EXPORT_TYPE)->dict:
        """Get the markup according to the export type."""
        if exportType == EXPORT_TYPE.RAW:
            color = cls.PLOT["DATA_COLOR"]
            label = cls.PLOT["RAW_DATA_LABEL"]
        elif exportType == EXPORT_TYPE.PROCESSED:
            color = cls.PLOT["DATA_COLOR"]
            label = cls.PLOT["PROCESSED_DATA_LABEL"]
        elif exportType == EXPORT_TYPE.BATCH:
            color = None
            label = cls.PLOT["BATCH_DATA_LABEL"]
        elif exportType == cls.BASELINE:
            color = cls.PLOT["BASELINE_COLOR"]
            label = cls.PLOT["BASELINE_LABEL"]
        markup = {"color": color, "label": label}
        return markup


    @classmethod
    def determine_color(cls, integrationArea:Integration)->str:
        peakColor = cls.PLOT["INT_PEAK_COLOR"]
        referenceColor = cls.PLOT["INT_REF_COLOR"]
        isPeakType = (integrationArea.peakType == CHC.TYPE_PEAK)
        col = peakColor if isPeakType else referenceColor
        return col


    ## __methods__

    def __init__(self, uiElement:MatplotlibWidget, exportType:EXPORT_TYPE)->None:
        self._logger = logging.getLogger(self.__class__.__name__)

        self._ui = uiElement
        self._exportType = exportType

        self._labels = self.get_labels(self._exportType)
        self._markup = self.get_markup(self._exportType)

        self.data = np.zeros(shape=(0, 2))
        self.integrationAreas = []


    def __repr__(self):
        info = {}
        info["ui"] = self._ui
        info["exportType"] = self._exportType
        info["labels"] = self._labels
        info["markup"] = self._markup
        info["has Baseline"] = hasattr(self, self.BASELINE)
        info["data length"] = f"X:{len(self.xData)}"
        return self.__module__ + ":\n" + str(info)


    ## methods

    def add_baseline(self, baselineData:np.ndarray)->None:
        """Adds the baseline of a spectrum as property (to plot)."""
        self._baseline = baselineData


    def set_data(self, xyData:np.ndarray, integrationAreas:list=None,
                 baselineData:np.ndarray=None)->None:
        """
        Updates the data of the spectrum.

        Set integration areas and baseline for more detailled plotting.
        """
        self.data = xyData
        self.integrationAreas = integrationAreas or []
        if not baselineData is None:
            self.add_baseline(baselineData)

        if self._exportType == EXPORT_TYPE.RAW :
            if uni.data_are_pixel(self.xData):
                self._labels = self.get_labels(EXPORT_TYPE.RAW)
            else:
                self._labels = self.get_labels(EXPORT_TYPE.PROCESSED)

        self.plot_spectrum()


    def plot_spectrum(self)->None:
        self.init_plot()
        self.update_plot()


    def init_plot(self)->None:
        """Inits the plots in the ui element regarding e.g. labels."""
        self.reset_plot()
        self._ui.axes.update_layout(**self._labels)


    def reset_plot(self)->None:
        self._ui.axes.clear()
        self._ui.axes.axhline()
        self._ui.axes.axvline()


    def update_plot(self)->None:
        """Updates the plots in the ui element."""
        self._ui.axes.plot(*self.data.T, **self._markup)
        self.plot_baseline()
        self.plot_integration_areas()
        self._ui.draw()


    def plot_baseline(self)->None:
        try:
            baselineMarkup = self.get_markup(self.BASELINE)
            self._ui.axes.plot(self.xData, self._baseline, **baselineMarkup)
        except AttributeError:
            self._logger.info("Could not plot baseline.")


    def plot_integration_areas(self)->None:
        for intArea in self.integrationAreas:
            col = self.determine_color(intArea)
            self._ui.axes.fill_between(intArea.xData, intArea.yData, color=col)
