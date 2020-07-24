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

# third-party libs

# local modules/libs
from ConfigLoader import ConfigLoader
from Logger import Logger
from custom_types.Peak import Peak
from custom_types.ReferencePeak import ReferencePeak

# Enums
from custom_types.ERROR_FITTING import ERROR_FITTING as ERR

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
        """
        Load the currently selected fitting.

        Resets the error code, validates the fitting and make the properties
        accessible.

        """

        self.errCode = ""

        try:
            self.currentPeak = Peak(**fitting["PEAKS"])
        except KeyError:
            # In case of PEAKS is not defined:
            # KeyError: type object argument after ** must be a mapping, not NoneType
            self.errCode += ERR.FITTING.value
            self.logger.error("Error: Fitting has an error!")
            print("Error: Fitting has an error!")
        except TypeError:
            # In case of centralWavelngth/.. is not defined:
            # TypeError: __init__() missing 1 required positional argument: 'centralWavelength'
            self.logger.error("Invalid Peak")
            self.errCode += ERR.PEAK.value

        self.currentName = fitting.get("NAME", "No name defined!")
        self._currentFitting = fitting

    @property
    def currentPeak(self) -> Peak:
        return self._currentPeak

    @currentPeak.setter
    def currentPeak(self, peak):
        try:
                # Distinguish between
                # 1. No reference defined, which may be valid.
                # 2. Invalid defined reference -> Error code.
            if peak.reference:
                self.currentReference = ReferencePeak(**peak.reference)
        except TypeError:
            self.errCode += ERR.REFERENCE.value
            self.logger.warning("Invalid reference peak defined.")
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

    @property
    def errCode(self) -> str:
        error = self._errCode
        if error:
            error += "!"
        return error

    @errCode.setter
    def errCode(self, code:str):
        self._errCode = code
