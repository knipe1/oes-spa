#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 12:55:37 2021

@author: Hauke Wernecke
"""

# standard libs
import logging

# third-party libs

# local modules/libs
from .matplotlibwidget import MatplotlibWidget
from loader.configloader import ConfigLoader

# Enums




class Interface_MatplotlibWidget():

    # constants and configs
    PLOT = ConfigLoader().PLOT

    ## __methods__

    def __init__(self, uiElement:MatplotlibWidget)->None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._ui = uiElement
        self._reset_plot()

        self.labels = {}


    def __repr__(self):
        info = {}
        info["ui"] = self._ui
        return self.__module__ + ":\n" + str(info)


    ## methods

    def plot_spectrum(self)->None:
        self.init_plot()
        self.update_plot()


    def init_plot(self)->None:
        """Inits the plots in the ui element regarding e.g. labels."""
        self._remove_plots()
        self._ui.axes.update_layout(**self.labels)
        # Resets the color cycle, that the first line is always plotted in the same color.
        self._ui.axes.set_prop_cycle(None)


    def update_plot(self)->None:
        """Updates the plots in the ui element."""
        self._ui.axes.plot(*self.data.T, **self._markup)
        self._ui.draw()


    def _remove_plots(self)->None:
        lines = self._ui.axes.lines
        while len(lines) > 2:
            lines.remove(lines[-1])

        collections = self._ui.axes.collections
        while len(collections):
            collections.remove(collections[-1])


    def _reset_plot(self)->None:
        self._ui.axes.clear()
        self._ui.axes.axhline()
        self._ui.axes.axvline()
