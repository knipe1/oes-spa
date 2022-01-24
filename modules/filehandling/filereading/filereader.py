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
import pandas as pd

# third-party libs

# local modules/libs
# FileFramework: base class.
from ..fileframework import FileFramework
# specific subReader
from .ascreader import AscReader
from .csvreader import CsvReader
from .sifreader import SifReader
from .spkreader import SpkReader
from ..filewriting.spectrumwriter import is_exported_spectrum
# further modules
import modules.universal as uni

# enums (alphabetical order)
from c_enum.asc_parameter import ASC_PARAMETER as ASC
from c_enum.error_code import ERROR_CODE as ERR
from c_enum.suffices import SUFFICES as SUFF

# exceptions
from exception.ParameterNotSetError import ParameterNotSetError


class FileReader(FileFramework):
    """
    Reads a spectrum file and provides an interface for data.

    Import XY data from different filetypes:
        *.spk/*.Spk
        *.asc
        *.csv
        *.sif
        *.ba

    Usage:


    Attributes
    ----------
    timestamp : datetime or None
        Date and Time formatted as defined in the configuration.
    data : nunpy.array
        Concats the x- & y-data. First column: x second column: y.
    WAVELENGTH : str
        The wavelength if specified in the paramter of the file.


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
    def WAVELENGTH(self):
        """Specific value of the parameter set."""
        try:
            wl = self.parameter[ASC.WL.value]
        except KeyError:
            raise ParameterNotSetError from KeyError
        return float(wl)


    ### __Methods__

    def __init__(self, filename, **kwargs):
        # FileFramework provides the dialect and config etc.
        super().__init__(filename)
        self.set_defaults()
        self.subReader = self.determine_subReader()
        if self.subReader is None:
            self.logger.info("No valid file: {self.filename}")
            return

        # self._logger.info("Read file: %s", self.filename)
        self.__post_init__(**kwargs)


    def __post_init__(self, **kwargs):
        self.read_file(**kwargs)


    def __bool__(self):
        return (self.is_valid_spectrum() == ERR.OK)


    def __repr__(self):
        info = {}
        info["filename"] = self.filename
        info["timeInfo"] = self.timeInfo
        return self.__module__ + ":\n" + str(info)


    ### Methods

    def set_defaults(self):
        self.data = None
        self.parameter = {}
        # Init with "Not set!" to display the warning on the ui.
        self.timeInfo = self.TIME_NOT_SET
        self.subReader = None


    def determine_subReader(self):
        _, _, suffix = uni.extract_path_basename_suffix(self.filename)

        if suffix == SUFF.CSV.value:
            subReader = CsvReader()
        elif suffix == SUFF.SPK.value:
            subReader = SpkReader()
        elif suffix == SUFF.ASC.value:
            subReader = AscReader()
        elif suffix == SUFF.SIF.value:
            subReader = SifReader()
        else:
            self._logger.warning("Unknown suffix: %s.", suffix)
            return None

        return subReader


    def is_valid_spectrum(self)->ERR:
        # Filetype.
        if not self.subReader:
            return ERR.UNKNOWN_FILETYPE

        # Data in general.
        if self.data is None or not len(self.data):
            return ERR.INVALID_DATA

        # Check file information.
        if not self.timeInfo or self.timeInfo == self.TIME_NOT_SET:
            return ERR.INVALID_FILEINFORMATION

        if not all((isinstance(d, (float, int)) for d in self.data[0, :])):
            return ERR.INVALID_DATA

        return ERR.OK


    def is_analyzable(self)->bool:
        return not is_exported_spectrum(self.filename)


    def read_file(self, **kwargs)->ERR:
        try:
            fileinformation = self.subReader.readout_file(self.filename)
        except (AttributeError, pd.errors.ParserError):
            return

        self.timeInfo = fileinformation["timeInfo"]
        self.data = fileinformation["data"]
        self.parameter = fileinformation.get("parameter", {})
