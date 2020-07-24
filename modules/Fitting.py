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
        self.__post_init__()


    def __post_init__(self):
        self.errCode or self.__validate__()


    def __repr__(self):
        info = {}
        info["currentFitting"] = self.currentFitting
        return self.__module__ + ":\n" + str(info)

    def __validate__(self):
        # Checks that the name is given.
        try:
            self.currentFitting["NAME"]
        except KeyError as err:
            key = err.args[0]
            self.logger.error("KeyError: {} not found in currently selected "\
                              "fitting.".format(key))
            print("KeyError: {} not found in currently selected "\
                              "fitting.".format(key))

        # Validation of the peak and the reference peak.
        # Validate reference only if peak is already valid.
        try:
            if not self.currentPeak.isValid:
                self.logger.error("Invalid Peak")

            # Checks that the reference peak is valid.
            try:
                # Distinguish between
                # 1. No reference defined, which may be valid.
                # 2. Invalid defined reference -> Error code.
                if self.currentReference and not self.currentReference.isValid:
                    self.logger.error("Invalid reference peak.")
            except AttributeError:
                self.errCode += ERR.REFERENCE.value
                self.logger.warning("No reference peak found.")

        except AttributeError:
            self.errCode += ERR.PEAK.value
            self.logger.error("No peak found.")


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
            # Handled in Peak validation
            pass

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

    @property
    def errCode(self) -> str:
        error = self._errCode
        if error:
            error += "!"
        return error

    @errCode.setter
    def errCode(self, code:str):
        self._errCode = code
