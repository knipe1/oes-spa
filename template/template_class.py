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

    # Set up the logger.
    logger = Logger(__name__)

    def __init__(self):
        pass

    def __post_init__(self):
        pass