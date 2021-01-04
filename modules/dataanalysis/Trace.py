#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 21:39:59 2020

@author: hauke
"""

# standard libs
from datetime import datetime
import numpy as np

# third-party libs

# local modules/libs
from modules.dataanalysis.Spectrum import Spectrum
import modules.Universal as uni
from ui.matplotlibwidget import MatplotlibWidget


# Enums
from c_enum.EXPORT_TYPE import EXPORT_TYPE



class Trace(Spectrum):

    @property
    def data(self)->np.ndarray:
        return self._data

    @data.setter
    def data(self, xyData)->None:
        self._data = xyData


    def __init__(self, uiElement:MatplotlibWidget):
        super().__init__(uiElement, EXPORT_TYPE.BATCH, name=__name__)


    def update_plot(self)->None:
        """Updates the plots in the ui element."""

        for peak in self.data.keys():
            self.markup["label"] = peak
            xData = self.data[peak][:, 0]
            yData = self.data[peak][:, 1]
            self.ui.axes.plot(xData, yData, **self.markup);

        try:
            self.center_plot(xData)
        except UnboundLocalError:
            pass
        self.ui.draw()


    def center_plot(self, xData)->None:
        leftLimit = xData[0]
        rightLimit = xData[-1]
        isSingleValue = (leftLimit == rightLimit)
        if not isSingleValue:
            self.ui.axes.update_layout(xLimit=(leftLimit, rightLimit));


    ## Calculation

    def calculate_time_differences(self, timestamps:tuple)->np.ndarray:
        diffTimes = [self.get_timediff_H(timestamp) for timestamp in timestamps]
        return np.array(diffTimes)


    def reset_time(self)->None:
        try:
            del self.referenceTime
        except AttributeError:
            pass


    def get_timediff_H(self, timestamp:datetime)->None:
        try:
            refTime = self.referenceTime
        except AttributeError:
            refTime = timestamp
            self.referenceTime = refTime

        diffTime = uni.convert_to_hours(timestamp - refTime)

        return diffTime



    ## Recording

    def plot_referencetime_of_spectrum(self, filename:str, timestamp:datetime)->None:
        try:
            relativeTime = self.get_timediff_H(timestamp)
        except TypeError:
            return
        reducedFilename = ''.join(uni.reduce_path([filename]))
        self.remove_recording()
        markup = {"color": self.PLOT["REFERENCE_COLOR"],
                  "linestyle": self.PLOT["REFERENCE_LINESTYLE"],
                  "label": reducedFilename,}
        self.recordingPlot = self.ui.axes.axvline(x=relativeTime, **markup)
        self.ui.draw()


    def remove_recording(self)->None:
        try:
            self.recordingPlot.remove()
        except AttributeError:
            pass


    def set_custom_yLabel(self, label:str)->None:
        arbitraryUnit = " / a. u."
        self.labels["yLabel"] = label + arbitraryUnit
        self.markup["label"] = label

