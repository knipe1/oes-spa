#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 13:29:10 2021

@author: Hauke Wernecke
"""



# standard libs

# third-party libs


# local modules/libs
from .interface_matplotlibwidget import Interface_MatplotlibWidget
from .matplotlibwidget import MatplotlibWidget
import modules.universal as uni


# Enums




class Multibatch_Canvas(Interface_MatplotlibWidget):

    def __init__(self, uiElement:MatplotlibWidget)->None:
        super().__init__(uiElement)

        self.labels = {
            "xLabel": self.PLOT["BATCH_X_LABEL"],
            "yLabel": self.PLOT["BATCH_Y_LABEL"],
        }


    def plot(self, data:list):
        self.init_plot()
        for xy, label in data:
            self._ui.axes.plot(*xy, label=label)
        self._ui.axes.legend()
        self._ui.draw()
