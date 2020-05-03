#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 09:17:47 2020

@author: hauke
"""


# standard libs
import yaml

# third-party libs

# local modules/libs

# Enums

class ConfigLoader():

    ### Properties - Getter & Setter

    @property
    def path(self) -> str:
        """path getter."""
        return self._path

    @path.setter
    def path(self, pathname:str):
        """path setter."""
        # If pathname is either not a string or is but is empty, this pathname
        # is invalid.
        if isinstance(pathname, str) and pathname:
            self._path = pathname


    @property
    def BATCH(self) -> dict:
        """Get the BATCH-configuration."""
        return self.config["BATCH"]

    @property
    def DATA_STRUCTURE(self) -> dict:
        """Get the DATA_STRUCTURE-configuration."""
        return self.config["DATA_STRUCTURE"]

    @property
    def DIALECT(self) -> dict:
        """Get the DIALECT-configuration."""
        return self.config["DIALECT"]

    @property
    def EXPORT(self) -> dict:
        """Get the EXPORT-configuration."""
        return self.config["EXPORT"]

    @property
    def FILE(self) -> dict:
        """Get the FILE-configuration."""
        return self.config["FILE"]

    @property
    def FITTING(self) -> dict:
        """Get the FITTING-configuration."""
        return self.config["FITTING"]

    @property
    def IMPORT(self) -> dict:
        """Get the IMPORT-configuration."""
        return self.config["IMPORT"]

    @property
    def MARKER(self) -> dict:
        """Get the MARKER-configuration."""
        return self.config["MARKER"]

    @property
    def PLOT(self) -> dict:
        """Get the PLOT-configuration."""
        return self.config["PLOT"]


    ### Methods

    def __init__(self, path:str = "./config.yml"):
        self.path = path;
        self.config = self.load_config()


    def load_config(self):
        """"Load a config from a yml file."""
        with open(self.path, "r", newline='') as ymlFile:
            config = yaml.load(ymlFile, Loader=yaml.FullLoader)
        return config


    def save_config(self, conf: dict):
        """"Save a config to a yml file."""
        with open(self.path, "w", newline='') as ymlFile:
            config = yaml.dump(conf, ymlFile)
        return config