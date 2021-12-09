#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 15:04:01 2021

@author: hauke
"""

# standard libs
import yaml

# third-party libs

# local modules/libs

# Enums

class YamlLoader():

    ### Methods

    def __init__(self, path:str):
        self._path = path
        self.config = self.load_config()


    def load_config(self):
        """"Load a config from a yml file."""
        try:
            with open(self._path, "r") as ymlFile:
                config = yaml.load(ymlFile, Loader=yaml.FullLoader)
            return config
        except yaml.parser.ParserError:
            print(f"Could not open configuration. Invalid formatted! Path is: {self._path}")
            return {}
        except FileNotFoundError:
            print("File not found! Path is: {self._path}")
            return {}



    def save_config(self):
        """"Save a config to a yml file."""
        with open(self._path, "w") as ymlFile:
            yaml.dump(self.config, ymlFile)
