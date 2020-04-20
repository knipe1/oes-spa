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
from PyQt5 import QtCore #test

# local modules/libs
import modules.Universal as uni
from Logger import Logger

# Enums

class Fitting(QtCore.QObject):
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

    #### test
    test = QtCore.pyqtSignal(str)

    def do_signal(self):
        self.test.emit("Hi")
    #####

    def __init__(self, fittings):
        QtCore.QObject.__init__(self)
        self.fittings = fittings

    ### Properties
    @property
    def currentFitting(self) -> dict:
        """currentFitting getter"""
        return self._currentFitting

    @currentFitting.setter
    def currentFitting(self, fitting):
        # TODO: doublecheck
        self.logger.info("current fitting:")
        self.logger.info(fitting)
        self._currentFitting = fitting


    def load_current_fitting(self, fitting_name:str) -> dict:
        """
        Retrieve the config of the currently selected fitting.

        Parameters
        ----------
        fitting_name : str
            The name of the selected fitting within the ui element.

        Returns
        -------
        fitConfig : dict
            Contains the config of the selected fitting.

        """
        # TODO: another function? if so, use current_fitting as property
        # and use the other funtion?
        # TODO: check out the class Peak!
        # get the selected fitting
        self.logger.info("load current fitting")
        for fit, name in self.fittings.items():
            if name == fitting_name:
                current_fit = fit
                break

        # load the config from the file and set the current config
        path = os.path.join(self.FITTING["DIR"], current_fit)
        fitConfig = uni.load_config(path)

        self.currentFitting = fitConfig


    def calculate_characteristic_value(self):
        # calculating the value if references are given
        # and checking against the minimum value
        pass
