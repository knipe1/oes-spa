#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# TODO: docstring

Created on Sat Apr 25 2020

@author: Hauke Wernecke
"""

# standard libs
import numpy as np

# third-party libs

# local modules/libs
from ConfigLoader import ConfigLoader
from Logger import Logger

# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE

class Spectrum():
    """
    Concentrate properties for handling spectra.

    Usage:
        TODO

    Attributes
    ----------
    ui: matplotlibwidget
        An ui-element to plot the spectrum.
    exportType: EXPORT_TYPE
        The exportType defines further properties like labels, markup,...
    xData:
        TODO: Doublecheck TODO in the method updateData
    yData:
        TODO: Doublecheck TODO in the method updateData
    labels: dict
        Contains x- and y-label.
    markup:dict
        Contains label, color,...


    Methods
    -------
    get_labels(cls, exportType):
        Get the labels according to the export type.
    get_markup(cls, exportType):
        Get the markup according to the export type.
    add_baseline(self, baseline):
        Adding the baseline of a spectrum as property (to plot).
    update_data(self, xData, yData):
        Updates the data of the spectrum.

    """
    # Load the configuration for plotting properties.
    config = ConfigLoader()
    PLOT = config.PLOT;

    # set up the logger
    logger = Logger(__name__)

    BASELINE = "baseline"

    @property
    def data(self):
        return (self.xData, self.yData)

    @classmethod
    def get_labels(cls, exportType):
        """Get the labels according to the export type."""
        labels = {};
        if exportType == EXPORT_TYPE.RAW:
            labels = {"xLabel":cls.PLOT["RAW_X_LABEL"],
                      "yLabel":cls.PLOT["RAW_Y_LABEL"]}
        elif exportType == EXPORT_TYPE.PROCESSED:
            labels = {"xLabel":cls.PLOT["PROCESSED_X_LABEL"],
                      "yLabel":cls.PLOT["PROCESSED_Y_LABEL"]}
        return labels


    @classmethod
    def get_markup(cls, exportType):
        """Get the markup according to the export type."""
        markup = {};
        if exportType == EXPORT_TYPE.RAW:
            markup = {"color": cls.PLOT["RAW_DATA_COLOR"],
                      "label": cls.PLOT["RAW_DATA_LABEL"]}
        elif exportType == EXPORT_TYPE.PROCESSED:
            markup = {"color": cls.PLOT["PROCESSED_DATA_COLOR"],
                      "label": cls.PLOT["PROCESSED_DATA_LABEL"]}
        elif exportType == cls.BASELINE:
            markup = {"color": cls.PLOT["RAW_BASELINE_COLOR"],
                      "linestyle": cls.PLOT["RAW_BASELINE_STYLE"],
                      "label": cls.PLOT["RAW_BASELINE_LABEL"]}
        return markup


    def __init__(self, uiElement, exportType, xData=[], yData=[], baseline=[]):

        # TODO: validation of uiElement? Or: Remove validation of exportType?
        # Depending on the implementation, it will run in an error.
        self.ui = uiElement;
        if not isinstance(exportType, EXPORT_TYPE):
            raise TypeError("Invalid instance of Spectrum-object!")
        self.exportType = exportType;
        self.xData = xData;
        self.yData = yData;
        self.labels = self.get_labels(exportType)
        self.markup = self.get_markup(exportType)
        self.add_baseline(baseline)

    def add_baseline(self, baseline):
        """Adding the baseline of a spectrum as property (to plot)."""
        self.baseline = baseline;
        if len(baseline):
            self.baselineMarkup = self.get_markup(self.BASELINE)

    def update_data(self, xData, yData):
        """Updates the data of the spectrum."""
        # TODO: option: add validation here.
        # E.g. equal length or use numpy array here?
        self.xData = np.array(xData)
        self.yData = np.array(yData)


    def init_plot(self):
        """Inits the plots in the ui element regarding e.g. labels."""

        if self.exportType == EXPORT_TYPE.BATCH:
            import matplotlib.dates as mdates
            self.ui.axes.xaxis_date()
            self.ui.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        axes = self.ui.axes
        labels = self.labels

        # Reset plot.
        axes.clear();
        # Add a coordinate origin with default markup.
        axes.axhline()
        axes.axvline()
        # Update the labels of the plot.
        axes.update_layout(**labels)


    def update_plot(self):
        """Updates the plots in the ui element."""
        # TODO: errorhandling

        if self.exportType == EXPORT_TYPE.BATCH:
            import matplotlib.dates as mdates
            self.ui.axes.xaxis_date()
            self.ui.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        axes = self.ui.axes

        # Plot the data and eventually a baseline.
        axes.plot(self.xData, self.yData, **self.markup);
        if len(self.baseline):
            axes.plot(self.xData, self.baseline, **self.baselineMarkup);

        # Zoom to specific area.
        axes.update_layout(xLimit=(self.xData[0], self.xData[-1]));

        self.ui.draw()
