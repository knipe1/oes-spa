#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 09:17:47 2020

@author: hauke
"""


# standard libs
import os
import shutil

# third-party libs

# local modules/libs
from loader.yamlloader import YamlLoader
from c_metaclass.singleton import Singleton

# Enums

class ConfigLoader(YamlLoader, metaclass=Singleton):
    DEFAULT_CONFIG = "./default_config.yml"

    ### Properties - Getter & Setter

    @property
    def BATCH(self) -> dict:
        """Get the BATCH-configuration."""
        return self.config["BATCH"]

    @property
    def GENERAL(self) -> dict:
        """Get the FILE-configuration."""
        return self.config["GENERAL"]

    @property
    def FITTING(self) -> dict:
        """Get the FITTING-configuration."""
        return self.config["FITTING"]

    @property
    def PLOT(self) -> dict:
        """Get the PLOT-configuration."""
        return self.config["PLOT"]

    @property
    def SETTINGS(self) -> dict:
        """Get the SETTINGS-configuration."""
        return self.config["SETTINGS"]


    # Set indiviual props to update them properly.
    @property
    def logFile(self):
        return self.GENERAL.get("LOG_FILE")

    @logFile.setter
    def logFile(self, logfile:str):
        self.config["GENERAL"]["LOG_FILE"] = logfile


    @property
    def wavelength(self):
        return self.SETTINGS["WL"]

    @wavelength.setter
    def wavelength(self, wl:float):
        self.config["SETTINGS"]["WL"] = wl


    @property
    def dispersion(self):
        return self.SETTINGS["DISPERSION"]

    @dispersion.setter
    def dispersion(self, dp:float):
        self.config["SETTINGS"]["DISPERSION"] = dp


    @property
    def calibration(self)->bool:
        # Providing a default value for backwards compatibility.
        return self.SETTINGS.get("CALIBRATION", True)

    @calibration.setter
    def calibration(self, cal:bool):
        self.config["SETTINGS"]["CALIBRATION"] = cal


    @property
    def PRESELECT_FITTING(self):
        return self.FITTING["PRESELECT_FITTING"]

    @PRESELECT_FITTING.setter
    def PRESELECT_FITTING(self, fittingName:str)->None:
        self.config["FITTING"]["PRESELECT_FITTING"] = fittingName


    @property
    def CHECKED_FITTINGS(self):
        return self.FITTING["CHECKED_FITTINGS"]

    @CHECKED_FITTINGS.setter
    def CHECKED_FITTINGS(self, fittingNames:list)->None:
        self.config["FITTING"]["CHECKED_FITTINGS"] = fittingNames


    ### Methods

    def __init__(self, path:str = "./config.yml"):
        if not os.path.exists(path):
            shutil.copyfile(self.DEFAULT_CONFIG, path)
        super().__init__(path)
