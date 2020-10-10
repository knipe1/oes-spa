#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Created on Sat Apr 25 2020

@author: Hauke Wernecke
"""

# standard libs
import numpy as np

# third-party libs

# local modules/libs
from ConfigLoader import ConfigLoader
from Logger import Logger
import modules.Universal as uni


# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC


class Spectrum():
    """
    Concatenate properties of a spectrum to have data and plot abilities together.

    Usage:
        from modules.Spectrum import Spectrum
        spectrum = Spectrum(matplotlibwidget, EXPORT_TYPE)
        spectrum.update_data(data)
        spectrum.plot_spectrum()

    """
    # Load the configuration for plotting properties.
    config = ConfigLoader()
    PLOT = config.PLOT;

    BASELINE = "baseline"

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, xyData):
        self._data = np.array(xyData).transpose()

    @property
    def xData(self):
        return self._data[:, 0]

    @property
    def yData(self):
        return self._data[:, 1]

    @classmethod
    def get_labels(cls, exportType):
        """Get the labels according to the export type."""
        if exportType == EXPORT_TYPE.RAW:
            labels = {"xLabel":cls.PLOT["RAW_X_LABEL"],
                      "yLabel":cls.PLOT["RAW_Y_LABEL"]}
        elif exportType == EXPORT_TYPE.PROCESSED:
            labels = {"xLabel":cls.PLOT["PROCESSED_X_LABEL"],
                      "yLabel":cls.PLOT["PROCESSED_Y_LABEL"]}
        elif exportType == EXPORT_TYPE.BATCH:
            labels = {"xLabel":cls.PLOT["BATCH_X_LABEL"],
                      "yLabel":cls.PLOT["BATCH_Y_LABEL"]}
        return labels


    @classmethod
    def get_markup(cls, exportType):
        """Get the markup according to the export type."""
        if exportType == EXPORT_TYPE.RAW:
            markup = {"color": cls.PLOT["RAW_DATA_COLOR"],
                      "label": cls.PLOT["RAW_DATA_LABEL"]}
        elif exportType == EXPORT_TYPE.PROCESSED:
            markup = {"color": cls.PLOT["PROCESSED_DATA_COLOR"],
                      "label": cls.PLOT["PROCESSED_DATA_LABEL"]}
        elif exportType == EXPORT_TYPE.BATCH:
            markup = {"color": cls.PLOT["BATCH_DATA_COLOR"],
                      "label": cls.PLOT["BATCH_DATA_LABEL"]}
        elif exportType == cls.BASELINE:
            markup = {"color": cls.PLOT["RAW_BASELINE_COLOR"],
                      "linestyle": cls.PLOT["RAW_BASELINE_STYLE"],
                      "label": cls.PLOT["RAW_BASELINE_LABEL"]}
        return markup


    def __init__(self, uiElement, exportType):
        # Set up the logger.
        self.logger = Logger(__name__)

        self.ui = uiElement
        self.exportType = exportType

        self.labels = self.get_labels(exportType)
        self.markup = self.get_markup(exportType)


    def __repr__(self):
        info = {}
        info["ui"] = self.ui
        info["exportType"] = self.exportType
        info["labels"] = self.labels
        info["markup"] = self.markup
        info["has Baseline"] = self.hasattr("baseline")
        info["data length"] = "X:{}, Y:{}".format(len(self.xData), len(self.yData))
        return self.__module__ + ":\n" + str(info)


    def add_baseline(self, baseline):
        """Adds the baseline of a spectrum as property (to plot)."""
        self.baseline = baseline;
        self.baselineMarkup = self.get_markup(self.BASELINE)


    def update_data(self, xyData, integrationAreas:list=None, baselineData=None):
        """
        Updates the data of the spectrum.

        Set integration areas and baseline for more detailled plotting.
        """
        self.data = xyData
        self.integrationAreas = integrationAreas or []
        if not baselineData is None:
            self.add_baseline(baselineData)

        if uni.data_are_pixel(self.xData):
            self.labels = self.get_labels(EXPORT_TYPE.RAW)
        else:
            self.labels = self.get_labels(EXPORT_TYPE.PROCESSED)


    def set_custom_y_label(self, label):
        arbitraryUnit = " / a. u."
        self.labels["yLabel"] = label + arbitraryUnit
        self.markup["label"] = label
        self.ui.axes.update_layout(**self.labels)


    def plot_spectrum(self):
        self.init_plot()
        self.update_plot()


    def init_plot(self):
        """Inits the plots in the ui element regarding e.g. labels."""
        self.reset_plot()
        self.ui.axes.update_layout(**self.labels)


    def reset_plot(self):
        self.ui.axes.clear()
        self.ui.axes.axhline()
        self.ui.axes.axvline()


    def update_plot(self):
        """Updates the plots in the ui element."""

        self.ui.axes.plot(self.xData, self.yData, **self.markup);
        self.plot_baseline()
        self.plot_integration_areas()
        self.center_plot()
        self.ui.draw()


    def center_plot(self):
        """Centers the plot"""
        leftLimit = self.xData[0]
        rightLimit = self.xData[-1]
        try:
            self.ui.axes.update_layout(xLimit=(leftLimit, rightLimit));
        except:
            pass


    def plot_baseline(self):
        try:
            self.ui.axes.plot(self.xData, self.baseline, **self.baselineMarkup);
        except:
            self.logger.warning("Could not plot baseline.")


    def plot_integration_areas(self):
        peakColor = self.PLOT["INT_PEAK_COLOR"]
        referenceColor = self.PLOT["INT_REF_COLOR"]

        for intArea in self.integrationAreas:
            col = peakColor if intArea.peakType == CHC.TYPE_PEAK else referenceColor
            self.ui.axes.fill_between(intArea.xData, intArea.yData, color=col)



    def get_timediff_H(self, timestamp):
        try:
            refTime = self.referenceTime
        except:
            refTime = timestamp
            self.referenceTime = refTime

        diffTime = uni.convert_to_hours(timestamp - refTime)

        return diffTime


    def plot_reference(self, filename, timestamp):
        relativeTime = self.get_timediff_H(timestamp)
        reducedFilename = ''.join(uni.reduce_path([filename]))
        self.remove_reference()
        markup = {"color": self.PLOT["REFERENCE_COLOR"],
                  "linestyle": self.PLOT["REFERENCE_LINESTYLE"],
                  "label": reducedFilename,}
        self.referencePlot = self.ui.axes.axvline(x=relativeTime, **markup)
        self.ui.draw()

    def remove_reference(self):
        try:
            self.referencePlot.remove()
        except:
            pass

