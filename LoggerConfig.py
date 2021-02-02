#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 10:50:52 2021

@author: hauke
"""


# standard libs
import logging
import sys

# local modules/libs
from loader.ConfigLoader import ConfigLoader
from dialog_messages import dialog_logFile

# constants
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEF_LOG_FILE = "../debug.log"



def set_up()->None:
    filename = determine_filename()
    logging.basicConfig(level=LOG_LEVEL,
                        format=LOG_FORMAT,
                        handlers=[logging.FileHandler(filename),
                                  logging.StreamHandler(sys.stdout),]
                        )


def determine_filename()->str:
    filename = ConfigLoader().logFile
    if not filename:
        filename = dialog_logFile(defaultFile=DEF_LOG_FILE)

    try:
        with open(filename, "w"):
            pass
    except FileNotFoundError:
        filename = dialog_logFile(defaultFile=DEF_LOG_FILE)
    return filename
