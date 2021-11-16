#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for general purposes regarding read and write operations.

@author: Hauke Wernecke
"""

# standard libs
import logging
from datetime import datetime


class FileFramework:

    # constants
    TIME_NOT_SET = "Not set!"

    # Properties

    @property
    def timeInfo(self):
        return self._timestamp

    @timeInfo.setter
    def timeInfo(self, timestamp:datetime)->None:
        """Sets the timeinfo or the default value."""
        self._timestamp = timestamp or self.TIME_NOT_SET


    @property
    def fileinformation(self):
        return (self.filename, self.timeInfo)


    ## __methods__

    def __init__(self, filename:str)->None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self.filename = filename
        self.timeInfo = None
        self.data = None


    def __eq__(self, other):
        try:
            isEqual = (self.fileinformation == other.fileinformation)
        except AttributeError:
            # If compared with another type, that type has no header attribute.
            isEqual = False
        return isEqual


    def __repr__(self)->str:
        return self.__class__.__name__
