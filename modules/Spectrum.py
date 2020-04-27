#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# TODO: docstring

Created on Sat Apr 25 2020

@author: Hauke Wernecke
"""

# standard libs

# third-party libs

# local modules/libs
import modules.Universal as uni
from modules.Universal import ExportType
from Logger import Logger

# Enums

class Spectrum():

    # Getting the neccessary configs
    config = uni.load_config()
    PLOT = config.get("PLOT");

    # set up the logger
    logger = Logger(__name__)

    BASELINE = "baseline"

    @classmethod
    def get_labels(cls, exportType):
        labels = {};
        if exportType == ExportType.RAW:
            labels = {"xLabel":cls.PLOT["RAW_X_LABEL"],
                      "yLabel":cls.PLOT["RAW_Y_LABEL"]}
        elif exportType == ExportType.PROCESSED:
            labels = {"xLabel":cls.PLOT["PROCESSED_X_LABEL"],
                      "yLabel":cls.PLOT["PROCESSED_Y_LABEL"]}
        return labels


    @classmethod
    def get_markup(cls, exportType):
        markup = {};
        if exportType == ExportType.RAW:
            markup = {"color": cls.PLOT["RAW_DATA_COLOR"],
                      "label": cls.PLOT["RAW_DATA_LABEL"]}
        elif exportType == ExportType.PROCESSED:
            markup = {"color": cls.PLOT["PROCESSED_DATA_COLOR"],
                      "label": cls.PLOT["PROCESSED_DATA_LABEL"]}
        elif exportType == cls.BASELINE:
            markup = {"color": cls.PLOT["RAW_BASELINE_COLOR"],
                      "linestyle": cls.PLOT["RAW_BASELINE_STYLE"],
                      "label": cls.PLOT["RAW_BASELINE_LABEL"]}
        return markup


    def __init__(self, uiElement, exportType, xData=[], yData=[], baseline=[]):
        self.ui = uiElement;
        if not isinstance(exportType, ExportType):
            raise TypeError("Invalid instance of Spectrum-object!")
        self.exportType = exportType;
        self.xData = xData;
        self.yData = yData;
        self.labels = self.get_labels(exportType)
        self.markup = self.get_markup(exportType)
        self.add_baseline(baseline)

    def add_baseline(self, baseline):
        self.baseline = baseline;
        if len(baseline):
            self.baselineMarkup = self.get_markup(self.BASELINE)

    def update_data(self, xData, yData):
        # option: add validation here.
        self.xData = xData
        self.yData = yData

