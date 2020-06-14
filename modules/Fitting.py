#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# TODO: docstring

Created on Thu Apr  9 10:51:31 2020

@author: Hauke Wernecke
"""

# useful docs:
#   https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
#   https://doc.qt.io/qt-5/qcombobox.html

# standard libs
import os

# third-party libs
from PyQt5 import QtCore

# local modules/libs
from ConfigLoader import ConfigLoader
import modules.Universal as uni
from Logger import Logger
from custom_types.Peak import Peak
from custom_types.ReferencePeak import ReferencePeak

# Enums

class Fitting(QtCore.QObject):
    """
    # TODO: docstring
    Interface for properties of the current active fitting.

    Contains information about characteristic values, names, peaks and the
    corresponding reference peaks.


    Attributes
    ----------


    Methods
    -------
    load_current_fitting(fitting_name:str) -> dict:
        Retrieve the config of the currently selected fitting.

    """

    # Load the configuration for fitting properties.
    config = ConfigLoader()
    FITTING = config.FITTING;

    # Set up the logger.
    logger = Logger(__name__)

    # variables
    _fittings = {}


    def __init__(self, fitting):
        QtCore.QObject.__init__(self)
        self.currentFitting = fitting

    def __repr__(self):
        info = {}
        info["currentFitting"] = self.currentFitting
        return self.__module__ + ":\n" + str(info)

    ### Properties
    @property
    def currentFitting(self) -> dict:
        """currentFitting getter"""
        return self._currentFitting

    @currentFitting.setter
    def currentFitting(self, fitting):
        self.currentPeak = Peak(**fitting.get("PEAKS"))
        self.currentName = fitting.get("NAME")
        self._currentFitting = fitting

    @property
    def currentPeak(self) -> Peak:
        return self._currentPeak

    @currentPeak.setter
    def currentPeak(self, peak):
        try:
            self.currentReference = ReferencePeak(**peak.reference)
        except TypeError:
            self.logger.warning("No reference peak defined.")

        self._currentPeak = peak

    @property
    def currentReference(self) -> Peak:
        return self._currentReference

    @currentReference.setter
    def currentReference(self, reference):
        self._currentReference = reference

    @property
    def currentName(self) -> str:
        return self._currentName

    @currentName.setter
    def currentName(self, name):
        self._currentName = name


    # def load_current_fitting(self, fitting_name:str) -> dict:
    #     """
    #     Retrieve the config of the currently selected fitting.

    #     Can be connected to the signal of an ui element, e.g.
    #     "currentTextChanged".

    #     Parameters
    #     ----------
    #     fitting_name : str
    #         The name of the selected fitting within the ui element.

    #     Returns
    #     -------
    #     fitConfig : dict
    #         Contains the config of the selected fitting.

    #     """
    #     # TODO: another function? if so, use current_fitting as property
    #     # and use the other funtion?
    #     # TODO: check out the class Peak!
    #     # get the selected fitting
    #     self.logger.info("load current fitting")
    #     for fit, name in self.fittings.items():
    #         if name == fitting_name:
    #             current_fit = fit
    #             break

    #     # load the config from the file and set the current config
    #     path = os.path.join(self.FITTING["DIR"], current_fit)
    #     fitConfig = ConfigLoader(path)

    #     self.currentFitting = fitConfig.config
