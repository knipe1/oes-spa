#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for general purposes regarding read and write operations

Register a common  dialect and
defines the configurations
"""
# imports
import csv

import modules.Universal as uni

class FileFramework:
    # load config
    config = uni.load_config()
    SAVE = config["SAVE"]
    LOAD = config["LOAD"]
    MARKER = config["MARKER"]
    DIALECT = config["DIALECT"]

    def __init__(self):
        csv.register_dialect(self.DIALECT["name"],
                             delimiter = self.DIALECT["delimiter"],
                             quoting = self.DIALECT["quoting"])
        self.dialect = self.DIALECT["name"]