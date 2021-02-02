#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# TODO: docstring

Created on Thu Apr  9 10:51:31 2020

@author: Hauke Wernecke
"""

# standard libs
import logging

# third-party libs

# local modules/libs
from loader.ConfigLoader import ConfigLoader

# Enums

class name():

    # Load the configuration.
    config = ConfigLoader()


    ### Properties


    ### __Methods__

    def __init__(self):
        self._logger = logging.getLogger(__name__)

        self.__post_init__()

    def __post_init__(self):
        pass


    ### Methods

### module-level functions
