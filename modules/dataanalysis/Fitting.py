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

# Enums
from c_enum.ERROR_CODE import ERROR_CODE as ERR
from c_enum.ERROR_FITTING import ERROR_FITTING as ERR_FIT
from c_types.Peak import Peak


# constants
NO_NAME_DEFINED = "No name provided!"


class Fitting():
    """
    Interface for properties of the currently active fitting.

    Contains information about characteristic values, names, peaks and the
    corresponding reference peaks.

    """

    # Load the configuration for fitting properties.
    FITTING = ConfigLoader().FITTING;


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
        # Set up the logger.
        self.logger = Logger(__name__)

        self.reset_errorcode()

        name, calibration, peakParameter = self.extract_parameter(fitting)

        self.name = name
        self.calibration = calibration
        try:
            self.peak = self.set_peak(**peakParameter)
        except TypeError:
            self.update_errorcode_fitting()


    def __repr__(self):
        info = {}
        info["Name"] = self.name
        info["Calibration"] = self.calibration
        info["Peak"] = self.peak
        return self.__module__ + ":\n" + str(info)


    ## methods

    def extract_parameter(self, fitting:dict)->dict:

        fittingName = self.extract_fitting_name(fitting)
        calibration = self.extract_calibration(fitting)
        peakParameter = self.extract_peak_parameter(fitting)

        return fittingName, calibration, peakParameter


    def extract_fitting_name(self, fitting:dict)->str:
        name = fitting.get("NAME", NO_NAME_DEFINED)
        return name


    def extract_calibration(self, fitting:dict)->str:
        calibration = fitting.get("CALIBRATION")
        if calibration:
            calibration = self.FITTING["DIR"] + calibration
        return calibration


    def extract_peak_parameter(self, fitting:dict)->dict:
        peakParameter = fitting.get("PEAKS")
        return peakParameter


    # def set_peak(self, parameter:dict)->Peak:
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
            return None

        if hasValidReference is None:
            self.logger.info("No reference peak defined.")
        elif not hasValidReference:
            self.update_errorcode_reference()


    ## update errorcode/validation methods

    def is_valid(self)->bool:
        err = bool(self.errCode)
        return not err


    def update_errorcode_fitting(self)->None:
        self.errCode += ERR_FIT.FITTING.value
        self.logger.error("Error: Fitting has an error!")


    def update_errorcode_peak(self)->None:
        self.errCode += ERR_FIT.PEAK.value
        self.logger.error("Error: Peak is not properly defined!")


    def update_errorcode_reference(self)->None:
        self.errCode += ERR_FIT.REFERENCE.value
        self.logger.warning("Invalid reference peak defined.")


    def reset_errorcode(self)->None:
        self.errCode = ERR_FIT.OK.value
