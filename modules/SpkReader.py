#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:11:22 2020

@author: Hauke Wernecke
"""

# standard libs

# third-party libs

# local modules/libs
from modules.ConfigReader import ConfigReader

# Enums

class SpkReader(ConfigReader):

    ### Properties

    ### __Methods__

    def __init__(self):
        # Init baseclass providing defaults and config.
        ConfigReader.__init__(self)
        self.__post_init__()

    def __post_init__(self):
        self.set_spk_defaults()


    ### Methods

    def set_spk_defaults(self):
        # TODO: docstring
        self.dialect = self.DIALECT["name"]
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["SPK_DATA_COLUMN"]


    def get_header(self, row:list)->tuple:
        """
        Extracts the header of an exported (csv, and spk) file.


        Parameters
        ----------
        row: list
            Required. The row of the file containing the header information.

        Returns
        -------
        date, time: str, str
            The date and the time of the measurement of the spectrum.

        """
        _, date, time = row[0].split()
        return (date, time)


    def preprocess(self, fReader, **kwargs):
        """
        Read out the data of a .asc-file respective to its structure.

        Parameters
        ----------
        fReader : csv.reader-object
            Reader to iterate through the csv-file.

        Returns
        -------
        data: list
            Contain the pixel/intensity values.

        """

        next(fReader)   # skip header.
        next(fReader)   # skip units.

