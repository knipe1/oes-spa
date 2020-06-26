#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# TODO: docstring

Created on Thu Apr  9 10:51:31 2020

@author: Hauke Wernecke
"""

# standard libs

# third-party libs

# local modules/libs
from ConfigLoader import ConfigLoader
from Logger import Logger

# Enums

class name():

    # Load the configuration.
    config = ConfigLoader()

    def __init__(self):

        # Set up the logger.
        self.logger = Logger(__name__)

        self.post_init__()

    def __post_init__(self):
        pass