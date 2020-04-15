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
import modules.Universal as uni
from Logger import Logger

# Enums

class Fitting():
    """
    # TODO: docstring
    summary line

    further information


    Attributes
    ----------


    Methods
    -------

    """


    # Getting the neccessary configs
    config = uni.load_config()
    FITTING = config["FITTING"];

    # set up the logger
    logger = Logger(__name__)

    # variables
    _fittings = {}

    def __init__(self, dropdown=None):
        self.dropdown = dropdown
        self.fittings = self.retrieve_fittings()
        self._currentFitting = self.load_current_fitting(dropdown.currentIndex())

    ### Properties

    @property
    def fittings(self):
        """fittings getter"""
        return self._fittings

    @fittings.setter
    def fittings(self, fits:dict):
        """fittings setter

        Updating the ui
        """
        self._fittings = fits
        # TODO: check condition?!?!?!
        if not self.dropdown == None:
            self.dropdown.clear()
            self.dropdown.addItems(fits.values())

    @property
    def currentFitting(self) -> dict:
        """currentFitting getter"""
        return self._currentFitting

    @classmethod
    def retrieve_fittings(cls) -> list:
        """
        Retrieve all fitting files of the directory of fittings.

        Returns
        -------
        fitList : list
            Containing the filenames of the fittings.

        """
        fitDict = {}
        # check out the default directory for fittings
        for _, _, f in os.walk(cls.FITTING["DIR"]):
            for file in f:
                # get the fitting files matching the pattern
                if file.rfind(cls.FITTING["FILE_PATTERN"]) > -1:
                    # loading the parameter and set up the dict using the
                    # filename and the name of the fitting
                    path = os.path.join(cls.FITTING["DIR"], file)
                    fitConfig = uni.load_config(path)
                    fitName = fitConfig.get("NAME")
                    fitDict[file] = fitName
        return fitDict

    def load_current_fitting(self, index:int) -> dict:
        """
        Retrieve the config of the currently selected fitting.

        Parameters
        ----------
        index : int
            The index of the selected fitting within the dropdown.

        Returns
        -------
        fitConfig : dict
            Contains the config of the selected fitting.

        """
        # TODO: another function? if so, use current_fitting as property
        # and use the other funtion?
        # TODO: check out the class Peak!
        text = self.dropdown.currentText()  # text as key of the dict
        # get the selected fitting
        for fit, name in self.fittings.items():
            if name == text:
                current_fit = fit
                break

        # TODO: dry: path and load config... see above
        path = os.path.join(self.FITTING["DIR"], current_fit)
        fitConfig = uni.load_config(path)

        return fitConfig

