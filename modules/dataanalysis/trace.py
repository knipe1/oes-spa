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
from .spectrum import Spectrum
import modules.universal as uni
from ui.matplotlibwidget import MatplotlibWidget

# Enums
from c_enum.export_type import EXPORT_TYPE



class Trace(Spectrum):

    @property
    def data(self)->np.ndarray:
        return self._data

    @data.setter
    def data(self, xyData)->None:
        self._data = xyData


    def __init__(self, uiElement:MatplotlibWidget):
        super().__init__(uiElement, EXPORT_TYPE.BATCH)


    def init_plot(self)->None:
        super().init_plot()
        self._delete_recording()


    def update_plot(self)->None:
        """Updates the plots in the ui element."""
        # Resets the color cycle, that the first line is always plotted in the same color.
        self._ui.axes.set_prop_cycle(None)
        for peak in self.data.keys():
            self._markup["label"] = peak
            self.data[peak] = self.sort_x_data(self.data[peak])
            self._ui.axes.plot(*self.data[peak].T, **self._markup)
        self._ui.draw()


    def sort_x_data(self, arr:np.ndarray):
        order = arr[:, 0].argsort()
        return arr[order]


    def reset_data(self):
        self.set_data({})


    ## Calculation

    def calculate_time_differences(self, timestamps:tuple)->np.ndarray:
        diffTimes = self.get_timediff_H(timestamps)
        return np.array(diffTimes)


    def get_timediff_H(self, timestamps:datetime)->None:
        try:
            refTime = self.referenceTime
        except AttributeError:
            refTime = timestamps[0]
            # refTime = timestamps[0].to_pydatetime()
        finally:
            self.referenceTime = refTime

        diffTime = uni.convert_to_hours(timestamps - refTime)
        return diffTime


    def reset_time(self)->None:
        try:
            del self.referenceTime
        except AttributeError:
            pass


    def trace_is_plotted(self)->None:
        return hasattr(self, "referenceTime")



    ## Recording

    def plot_referencetime_of_spectrum(self, filename:str, timestamp:datetime)->None:
        if not self.trace_is_plotted():
            return
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


    def _delete_recording(self)->None:
        try:
            del self.recordingPlot
        except AttributeError:
            pass



    def set_custom_yLabel(self, label:str)->None:
        arbitraryUnit = " / a. u."
        self.labels["yLabel"] = label + arbitraryUnit
