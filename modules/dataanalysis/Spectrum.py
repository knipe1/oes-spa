#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Created on Sat Apr 25 2020

@author: Hauke Wernecke
"""

# standard libs
import numpy as np
from datetime import datetime

# third-party libs

# local modules/libs
from ConfigLoader import ConfigLoader
from Logger import Logger
import modules.Universal as uni
from ui.matplotlibwidget import MatplotlibWidget


# Enums
from c_types.Integration import Integration
from c_enum.CHARACTERISTIC import CHARACTERISTIC as CHC
from c_enum.EXPORT_TYPE import EXPORT_TYPE


class Spectrum():
    """
    Concatenate properties of a spectrum to have data and plot abilities together.

    Usage:
        from modules.dataanalysis.Spectrum import Spectrum
        spectrum = Spectrum(matplotlibwidget, EXPORT_TYPE)
        spectrum.update_data(data)

    """
    # Load the configuration for plotting properties.
    config = ConfigLoader()
    PLOT = config.PLOT;

    BASELINE = "baseline"

    @property
    def data(self)->np.ndarray:
        return self._data

    @data.setter
    def data(self, xyData)->None:
        self._data = np.array(xyData)

    @property
    def xData(self)->np.ndarray:
        return self.data[:, 0]

    @property
    def yData(self)->np.ndarray:
        return self.data[:, 1]

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
            color = cls.PLOT["RAW_DATA_COLOR"]
            label = cls.PLOT["RAW_DATA_LABEL"]
        elif exportType == EXPORT_TYPE.PROCESSED:
            color = cls.PLOT["PROCESSED_DATA_COLOR"]
            label = cls.PLOT["PROCESSED_DATA_LABEL"]
        elif exportType == EXPORT_TYPE.BATCH:
            color = None
            label = cls.PLOT["BATCH_DATA_LABEL"]
        elif exportType == cls.BASELINE:
            color = cls.PLOT["RAW_BASELINE_COLOR"]
            label = cls.PLOT["RAW_BASELINE_LABEL"]
        markup = {"color": color, "label": label}
        return markup


    ## dunder methods

    def __init__(self, uiElement:MatplotlibWidget, exportType:EXPORT_TYPE)->None:
        # Set up the logger.
        self.logger = Logger(__name__)

        self.ui = uiElement
        self.exportType = exportType

        self.labels = self.get_labels(self.exportType)
        self.markup = self.get_markup(self.exportType)


    def __repr__(self):
        info = {}
        info["ui"] = self.ui
        info["exportType"] = self.exportType
        info["labels"] = self.labels
        info["markup"] = self.markup
        info["has Baseline"] = self.hasattr("baseline")
        info["data length"] = "X:%i, Y:%i"%(len(self.xData), len(self.yData))
        return self.__module__ + ":\n" + str(info)


    ## methods

    def add_baseline(self, baselineData:np.ndarray)->None:
        """Adds the baseline of a spectrum as property (to plot)."""
        self.baseline = baselineData;
        self.baselineMarkup = self.get_markup(self.BASELINE)


    def update_data(self, xyData:np.ndarray, integrationAreas:list=None, baselineData:np.ndarray=None)->None:
        """
        Updates the data of the spectrum.

        Set integration areas and baseline for more detailled plotting.
        """
        self.data = xyData
        self.integrationAreas = integrationAreas or []
        if baselineData is not None:
            self.add_baseline(baselineData)

        if self.exportType == EXPORT_TYPE.RAW :
            if uni.data_are_pixel(self.xData):
                self.labels = self.get_labels(EXPORT_TYPE.RAW)
            else:
                self.labels = self.get_labels(EXPORT_TYPE.PROCESSED)

        self.plot_spectrum()


    def plot_spectrum(self)->None:
        self.init_plot()
        self.update_plot()


    def init_plot(self)->None:
        """Inits the plots in the ui element regarding e.g. labels."""
        self.reset_plot()
        self.ui.axes.update_layout(**self.labels)


    def reset_plot(self)->None:
        self.ui.axes.clear()
        self.ui.axes.axhline()
        self.ui.axes.axvline()


    def update_plot(self)->None:
        """Updates the plots in the ui element."""

        self.ui.axes.plot(self.xData, self.yData, **self.markup);
        self.plot_baseline()
        self.plot_integration_areas()
        self.center_plot()
        self.ui.draw()


    def center_plot(self)->None:
        leftLimit = self.xData[0]
        rightLimit = self.xData[-1]
        isSingleValue = (leftLimit == rightLimit)
        if not isSingleValue:
            self.ui.axes.update_layout(xLimit=(leftLimit, rightLimit));


    def plot_baseline(self)->None:
        try:
            self.ui.axes.plot(self.xData, self.baseline, **self.baselineMarkup);
        except AttributeError:
            self.logger.info("Could not plot baseline.")


    def plot_integration_areas(self)->None:
        for intArea in self.integrationAreas:
            col = self.determine_color(intArea)
            self.ui.axes.fill_between(intArea.xData, intArea.yData, color=col)


    def determine_color(self, integrationArea:Integration)->str:
        peakColor = self.PLOT["INT_PEAK_COLOR"]
        referenceColor = self.PLOT["INT_REF_COLOR"]
        isPeakType = (integrationArea.peakType == CHC.TYPE_PEAK)
        col = peakColor if isPeakType else referenceColor
        return col

