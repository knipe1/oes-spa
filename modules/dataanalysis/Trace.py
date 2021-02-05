#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
class: Trace

@author: hauke
"""

# standard libs
import logging
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
        super().__init__(uiElement, EXPORT_TYPE.BATCH)


    def update_plot(self)->None:
        """Updates the plots in the ui element."""

        for peak in self.data.keys():
            self._markup["label"] = peak
            self._ui.axes.plot(*self.data[peak].T, **self._markup)
        self._ui.draw()


    def reset_data(self):
        self.set_data({})


    ## Calculation

    def calculate_time_differences(self, timestamps:tuple)->np.ndarray:
        diffTimes = [self.get_timediff_H(timestamp) for timestamp in timestamps]
        return np.array(diffTimes)


    def get_timediff_H(self, timestamp:datetime)->None:
        try:
            refTime = self.referenceTime
        except AttributeError:
            refTime = timestamp
            self.referenceTime = refTime

        diffTime = uni.convert_to_hours(timestamp - refTime)

        return diffTime


    def reset_time(self)->None:
        try:
            del self.referenceTime
        except AttributeError:
            pass



    ## Recording

    def plot_referencetime_of_spectrum(self, filename:str, timestamp:datetime)->None:
        try:
            # Handle incomplete/incorrect spectra.
            relativeTime = self.get_timediff_H(timestamp)
        except TypeError:
            return
        reducedFilename = uni.reduce_path(filename)
        self._remove_recording()
        markup = {"color": self.PLOT["REFERENCE_COLOR"],
                  "linestyle": self.PLOT["REFERENCE_LINESTYLE"],
                  "label": reducedFilename,}
        self.recordingPlot = self._ui.axes.axvline(x=relativeTime, **markup)
        self._ui.draw()


    def _remove_recording(self)->None:
        try:
            self.recordingPlot.remove()
        except AttributeError:
            pass


    def set_custom_yLabel(self, label:str)->None:
        arbitraryUnit = " / a. u."
        self.labels["yLabel"] = label + arbitraryUnit
