#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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

# Enums
from custom_types.ERROR_FITTING import ERROR_FITTING as ERR_FIT


# constants
NO_NAME_DEFINED = "No name provided!"



class Fitting():
    """
    # TODO: docstring
    Interface for properties of the currently active fitting.

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


    ### Properties

    @property
    def peak(self) -> Peak:
        return self._peak

    @peak.setter
    def peak(self, peak):
        self.set_peak_reference(peak)
        self._peak = peak
        return


    @property
    def errCode(self) -> str:
        error = self._errCode
        if error:
            error += "!"
        return error

    @errCode.setter
    def errCode(self, code:ERR_FIT):
        self._errCode = code


    ## __methods__

    def __init__(self, fitting):
        # Set up the logger.
        self.logger = Logger(__name__)

        self.fitting = fitting
        self.errCode = ERR_FIT.OK.value

        name, peakParameter = self.extract_parameter(fitting)

        self.name = name
        self.peak = self.set_peak(peakParameter)


    def __repr__(self):
        info = {}
        info["Fitting"] = self.fitting
        return self.__module__ + ":\n" + str(info)


    ## methods

    def extract_parameter(self, fitting:dict)->dict:

        fittingName = self.extract_fitting_name(fitting)
        peakParameter = self.extract_peak_parameter(fitting)

        return fittingName, peakParameter


    def extract_fitting_name(self, fitting:dict):
        name = fitting.get("NAME", NO_NAME_DEFINED)
        return name


    def extract_peak_parameter(self, fitting:dict):
        try:
            peakParameter = fitting["PEAKS"]
            return peakParameter
        except KeyError:
            # In case of PEAKS is not defined:
            # KeyError: type object argument after ** must be a mapping, not NoneType
            self.update_errorcode_fitting()


    def set_peak(self, peakParameter:dict)->Peak:
        try:
            peak = Peak(**peakParameter)
            return peak
        except TypeError:
            # In case an argument is not defined e.g.:
            # TypeError: __init__() missing 1 required positional argument: 'centralWavelength'
            self.update_errorcode_peak()


    def set_peak_reference(self, peak:Peak):
        try:
            if peak.reference is None:
                # 1. Invalid defined reference -> Error code.
                self.update_errorcode_reference()
            else:
                # 2. No reference defined, which is valid.
                self.reference = peak.reference
        except AttributeError:
            self.logger.info("No reference peak defined.")


    ## update errorcode methods

    def update_errorcode_fitting(self):
        self.errCode += ERR_FIT.FITTING.value
        self.logger.error("Error: Fitting has an error!")


    def update_errorcode_peak(self):
        self.errCode += ERR_FIT.PEAK.value
        self.logger.error("Error: Peak is not properly defined!")


    def update_errorcode_reference(self):
        self.errCode += ERR_FIT.REFERENCE.value
        self.logger.warning("Invalid reference peak defined.")