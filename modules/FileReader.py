#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Reader module

Import XY data from different filetypes:
    *.spk/*.Spk
    *.asc
    *.csv

Glossary:
    header: Information about the file itself (filename, date, time).


@author: Hauke Wernecke

"""

# standard libs
import csv
import numpy as np
from datetime import datetime
import fnmatch

# third-party libs

# local modules/libs
# FileFramework: base class.
from modules.FileFramework import FileFramework
# specific subReader
from modules.AscReader import AscReader
from modules.CsvReader import CsvReader
from modules.SpkReader import SpkReader
# further modules
import modules.Universal as uni

# enums (alphabetical order)
from custom_types.ASC_PARAMETER import ASC_PARAMETER as ASC
from custom_types.ERROR_CODE import ERROR_CODE as ERR
from custom_types.SUFFICES import SUFFICES as SUFF


class FileReader(FileFramework):
    """
    Reads a spectrum file and provides an interface for data.

    Import XY data from different filetypes:
        *.spk/*.Spk
        *.asc
        *.csv

    Usage:


    Attributes
    ----------
    timestamp : datetime or None
        Date and Time formatted as defined in the configuration.
    data : nunpy.array
        Concats the x- & y-data. First column: x; second column: y.
    header : tuple
        Gather the information about the file itself(name, date, time).
    WAVELENGTH : str
        The wavelength if specified in the paramter of the file.
    GRATING : str
        The grating if specified in the paramter of the file.


    Methods
    -------
    check_datafile()->ERROR_CODE:
        Checks whether the file contains valid data.
    determine_subReader()->str:
        Extracts the filetype of the given filename.
    read_file(**kwargs)->ERROR_CODE:
        TODO

    """

    ### Properties

    @property
    def timestamp(self)->datetime:
        """Formats date and time as defined in the configuration."""
        strTime = self.date + " " + self.time
        try:
            time = uni.timestamp_from_string(strTime)
        except ValueError:
            time = None
        return time


    @property
    def data(self)->tuple:
        """Concats the x- & y-data. First column: x; second column: y."""
        return (self.xData, self.yData)

    @data.setter
    def data(self, xyData):
        """Sets the x- & y-data. First column: x; second column: y."""
        xyData = np.array(xyData)
        try:
            self.xData = xyData[:, 0]
            self.yData = xyData[:, 1]
        except IndexError:
            self.logger.warning("No valid data given.")


    @property
    def header(self):
        """Gather the information about the file itself(name, date, time)."""
        return (self.filename, self.date, self.time)


    @property
    def fileinformation(self):
        return (self.filename, self.timestamp)


    @property
    def WAVELENGTH(self):
        """Specific value of the parameter set."""
        return self.parameter[ASC.WL.value]


    @property
    def GRATING(self):
        """Specific value of the parameter set."""
        return self.parameter[ASC.WL.value]


    ### __Methods__

    def __init__(self, filename, **kwargs):
        # FileFramework provides the dialect and config etc.
        super().__init__(filename)
        self.set_defaults()
        self.subReader = self.determine_subReader()

        self.__post_init__(**kwargs)
        self.logger.info("Read file: " + self.filename)


    def __post_init__(self, **kwargs):
        self.read_file(**kwargs)


    def __bool__(self):
        return (self.is_valid_spectrum() == ERR.OK)


    def __eq__(self, other):
        try:
            isEqual = (self.header == other.header)
        except AttributeError:
            # If compared with another type, that type has no header attribute.
            isEqual = False
        return isEqual


    def __repr__(self):
        info = {}
        info["Header"] = self.header
        info["Timestamp"] = self.timestamp
        info["data length"] = "X:%i, Y:%i"%(len(self.xData), len(self.yData))
        return self.__module__ + ":\n" + str(info)


    ### Methods

    def set_defaults(self):
        # TODO: Test None instead of 0
        self.xData = np.zeros(0)
        self.yData = np.zeros(0)
        self.parameter = {}
        # Init with "Not set!" to display the warning on the ui.
        self.date = "Not set!"
        self.time = "Not set!"
        self.subReader = None


    def determine_subReader(self):
        suffix = uni.get_suffix(self.filename)

        if suffix == SUFF.CSV.value:
            subReader = CsvReader()

        elif suffix == SUFF.SPK.value:
            subReader = SpkReader()

        elif suffix == SUFF.ASC.value:
            subReader = AscReader()

        else:
            self.logger.warning(f"Unknown suffix: {suffix}")
            return None

        return subReader


    def is_valid_spectrum(self)->ERR:
        errorcode = self.has_valid_frame()
        if not errorcode:
            return errorcode

        if not isinstance(self.xData[0], (float, int)):
            return ERR.INVALID_DATA

        return ERR.OK;


    def is_valid_batchfile(self)->ERR:
        errorcode = self.has_valid_frame()
        if not errorcode:
            return errorcode

        if not isinstance(self.xData[0], datetime):
            return ERR.INVALID_BATCHFILE

        return ERR.OK


    def has_valid_frame(self):
        # Filetype.
        if not self.subReader:
            return ERR.UNKNOWN_FILETYPE;

        # Data in general.
        if not len(self.xData):
            return ERR.INVALID_DATA;

        # Data that have same length.
        if len(self.xData) != len(self.yData):
            return ERR.DATA_UNEQUAL_LENGTH;

        # Check file information.
        if not self.timestamp:
            return ERR.INVALID_FILEINFORMATION;

        return ERR.OK



    def read_file(self, **kwargs)->ERR:

        with open(self.filename, 'r', newline='') as openFile:
            # Set up the reader (even if the file is something else than csv,
            # because we use another dialect then).
            fReader = csv.reader(openFile, dialect=self.subReader.dialect)
            fileinformation = self.subReader.readout_file(fReader, **kwargs)
            self.date, self.time = fileinformation["header"]
            self.data = fileinformation["data"]
            self.parameter = fileinformation.get("parameter", {})