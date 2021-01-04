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

# third-party libs

# local modules/libs
# FileFramework: base class.
from modules.filehandling.FileFramework import FileFramework
# specific subReader
from modules.filehandling.filereading.AscReader import AscReader
from modules.filehandling.filereading.BaReader import BaReader
from modules.filehandling.filereading.CsvReader import CsvReader
from modules.filehandling.filereading.SpkReader import SpkReader
from modules.filehandling.filewriting.SpectrumWriter import is_exported_spectrum
# further modules
import modules.Universal as uni

# enums (alphabetical order)
from c_enum.ASC_PARAMETER import ASC_PARAMETER as ASC
from c_enum.ERROR_CODE import ERROR_CODE as ERR
from c_enum.SUFFICES import SUFFICES as SUFF

# constants
TIME_NOT_SET = "Not set!"


class FileReader(FileFramework):
    """
    Reads a spectrum file and provides an interface for data.

    Import XY data from different filetypes:
        *.spk/*.Spk
        *.asc
        *.csv
        *.ba

    Usage:


    Attributes
    ----------
    timestamp : datetime or None
        Date and Time formatted as defined in the configuration.
    data : nunpy.array
        Concats the x- & y-data. First column: x; second column: y.
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
    def timeInfo(self):
        return self._timestamp

    @timeInfo.setter
    def timeInfo(self, timestamp:datetime):
        if not timestamp:
            timestamp = TIME_NOT_SET
        self._timestamp = timestamp


    @property
    def fileinformation(self):
        return (self.filename, self.timeInfo)


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
        super().__init__(filename, name=__name__)
        self.set_defaults()
        self.subReader = self.determine_subReader()

        self.__post_init__(**kwargs)
        self._logger.info("Read file: " + self.filename)


    def __post_init__(self, **kwargs):
        self.read_file(**kwargs)


    def __bool__(self):
        return (self.is_valid_spectrum() == ERR.OK)


    def __eq__(self, other):
        try:
            isEqual = (self.fileinformation == other.fileinformation)
        except AttributeError:
            # If compared with another type, that type has no header attribute.
            isEqual = False
        return isEqual


    def __repr__(self):
        info = {}
        info["filename"] = self.filename
        info["timeInfo"] = self.timeInfo
        info["data length"] = "X:%i, Y:%i"%(len(self.xData), len(self.yData))
        return self.__module__ + ":\n" + str(info)


    ### Methods

    def set_defaults(self):
        # TODO: Test None instead of 0
        # self.xData = np.zeros(0)
        # self.yData = np.zeros(0)
        self.xData = None
        self.yData = None
        self.data = None
        self.parameter = {}
        # Init with "Not set!" to display the warning on the ui.
        self.timeInfo = TIME_NOT_SET
        self.subReader = None


    def determine_subReader(self):
        suffix = uni.get_suffix(self.filename)

        if suffix == SUFF.CSV.value:
            subReader = CsvReader()

        elif suffix == SUFF.SPK.value:
            subReader = SpkReader()

        elif suffix == SUFF.ASC.value:
            subReader = AscReader()

        elif suffix == SUFF.BATCH.value:
            subReader = BaReader()

        else:
            self._logger.warning(f"Unknown suffix: {suffix}")
            return None

        return subReader


    def is_valid_spectrum(self)->ERR:
        errorcode = self.has_valid_frame()
        if not errorcode:
            return errorcode

        if isinstance(self.data, dict):
            return ERR.INVALID_DATA

        if not isinstance(self.data[0, 0], (float, int)):
            return ERR.INVALID_DATA

        return ERR.OK


    def is_valid_batchfile(self)->ERR:
        return self.has_valid_frame()


    def has_valid_frame(self):
        # Filetype.
        if not self.subReader:
            return ERR.UNKNOWN_FILETYPE;

        # Data in general.
        if self.data is None or not len(self.data):
            return ERR.INVALID_DATA;

        # Check file information.
        if not self.timeInfo:
            return ERR.INVALID_FILEINFORMATION;

        return ERR.OK


    def is_analyzable(self)->bool:
        return not is_exported_spectrum(self.filename)


    def read_file(self, **kwargs)->ERR:

        with open(self.filename, 'r', newline='') as openFile:
            # Set up the reader (even if the file is something else than csv,
            # because we use another dialect then).
            fReader = csv.reader(openFile, dialect=self.subReader.dialect)
            fileinformation = self.subReader.readout_file(fReader, **kwargs)
            self.timeInfo = fileinformation["timeInfo"]
            self.data = fileinformation["data"]
            self.parameter = fileinformation.get("parameter", {})