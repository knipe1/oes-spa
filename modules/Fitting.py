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

# local modules/libs
from ConfigLoader import ConfigLoader
import modules.Universal as uni
from Logger import Logger
from custom_types.Peak import Peak
from custom_types.ReferencePeak import ReferencePeak

# Enums

class Fitting():
    """
    # TODO: docstring
    Interface for properties of the current active fitting.

    Contains information about characteristic values, names, peaks and the
    corresponding reference peaks.


    Attributes
    ----------


    Methods
    -------

    """

    # Load the configuration for fitting properties.
    config = ConfigLoader()
    FITTING = config.FITTING;

    # variables
    _fittings = {}


    def __init__(self, fitting):
        # set up the logger
        self.logger = Logger(__name__)

        self.currentFitting = fitting
        self.__post_init__()


    def __post_init__(self):
        self.__validate__()


    def __repr__(self):
        info = {}
        info["currentFitting"] = self.currentFitting
        return self.__module__ + ":\n" + str(info)

    def __validate__(self):
        try:
            self.currentFitting["NAME"]
        except KeyError as err:
            key = err.args[0]
            self.logger.error("KeyError: {} not found in currently selected "\
                              "fitting.".format(key))
            print("KeyError: {} not found in currently selected "\
                              "fitting.".format(key))

        try:
            if not self.currentPeak.isValid:
                self.logger.error("Invalid Peak")
                print("Invalid Peak")
        except AttributeError:
            self.logger.error("No peak found.")
            print("No peak found.")

        try:
            if self.currentReference and not self.currentReference.isValid:
                self.logger.error("Invalid reference peak.")
                print("Invalid reference peak.")
        except AttributeError:
            self.logger.warning("No reference peak found.")
            print("No reference peak found.")


    ### Properties
    @property
    def currentFitting(self) -> dict:
        """currentFitting getter"""
        return self._currentFitting

    @currentFitting.setter
    def currentFitting(self, fitting):
        try:
            self.currentPeak = Peak(**fitting.get("PEAKS"))
        except TypeError as err:
            # In case of PEAKS is not defined:
            # TypeError: type object argument after ** must be a mapping, not NoneType
            # In case of centralWavelngth/.. is not defined:
            # TypeError: __init__() missing 1 required positional argument: 'centralWavelength'
            self.logger.error("Error: Fitting has an error!")
            print("Error: Fitting has an error!")

        self.currentName = fitting.get("NAME", "No name defined!")
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
