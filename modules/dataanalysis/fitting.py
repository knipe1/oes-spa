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
import logging

# third-party libs

# local modules/libs
from loader.ConfigLoader import ConfigLoader

# Enums
from c_enum.error_fitting import ERROR_FITTING as ERR_FIT
from c_types.Peak import Peak


# constants
NO_NAME_DEFINED = "No name provided!"

# Load the configuration for fitting properties.
FITTING = ConfigLoader().FITTING


class Fitting():
    """
    Interface for properties of the currently active fitting.

    Contains information about characteristic values, names, peaks and the
    corresponding reference peaks.

    """

    ### Properties

    @property
    def peak(self)->Peak:
        return self._peak

    @peak.setter
    def peak(self, peak)->None:
        self._peak = peak
        if not peak is None:
            self.check_peak_reference(peak)


    @property
    def errCode(self)->str:
        error = self._errCode
        if error:
            error += "!"
        return error

    @errCode.setter
    def errCode(self, code:ERR_FIT)->None:
        self._errCode = code


    ## __methods__

    def __init__(self, fitting:dict)->None:
        self._logger = logging.getLogger(self.__class__.__name__)

        self.reset_errorcode()

        name, calibration, peakParameter = extract_parameter(fitting)

        self.name = name
        self.calibration = calibration
        try:
            self.peak = self.set_peak(**peakParameter)
        except TypeError:
            self.peak = None
            self.update_errorcode_fitting()


    def __repr__(self):
        info = {}
        info["Name"] = self.name
        info["Calibration"] = self.calibration
        info["Peak"] = self.peak
        return self.__module__ + ":\n" + str(info)


    ## methods

    def set_peak(self, **kwargs)->Peak:
        try:
            peak = Peak(**kwargs)
            if not peak.isValid:
                self.update_errorcode_peak()
        except TypeError:
            # In case an argument is not defined e.g.:
            # TypeError: __init__() missing 1 required positional argument: 'centralWavelength'
            self.update_errorcode_peak()
            peak = None
        return peak


    def check_peak_reference(self, peak:Peak)->None:
        try:
            hasValidReference = peak.has_valid_reference()
        except ValueError:
            self.update_errorcode_reference()
            return

        if hasValidReference is None:
            self._logger.info("No reference peak defined.")
        elif not hasValidReference:
            self.update_errorcode_reference()


    ## update errorcode/validation methods

    def is_valid(self)->bool:
        err = bool(self.errCode)
        return not err


    def update_errorcode_fitting(self)->None:
        self.errCode += ERR_FIT.FITTING.value
        self._logger.error("Error: Fitting has an error!")


    def update_errorcode_peak(self)->None:
        self.errCode += ERR_FIT.PEAK.value
        self._logger.error("Error: Peak is not properly defined!")


    def update_errorcode_reference(self)->None:
        self.errCode += ERR_FIT.REFERENCE.value
        self._logger.warning("Invalid reference peak defined.")


    def reset_errorcode(self)->None:
        self.errCode = ERR_FIT.OK.value


def extract_parameter(fitting:dict)->dict:

    fittingName = extract_fitting_name(fitting)
    calibration = extract_calibration(fitting)
    peakParameter = extract_peak_parameter(fitting)

    return fittingName, calibration, peakParameter


def extract_fitting_name(fitting:dict)->str:
    name = fitting.get("NAME", NO_NAME_DEFINED)
    return name


def extract_calibration(fitting:dict)->str:
    calibration = fitting.get("CALIBRATION")
    if calibration:
        calibration = FITTING["DIR"] + calibration
    return calibration


def extract_peak_parameter(fitting:dict)->dict:
    peakParameter = fitting.get("PEAKS")
    return peakParameter
