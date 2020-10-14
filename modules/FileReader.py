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
        """
        Checks whether the file contains valid data.

        Returns
        -------
        ERROR_CODE

        """

        # Filetype.
        if not self.subReader:
            return ERR.UNKNOWN_FILETYPE;

        # Data in general.
        if not len(self.xData):
            return ERR.INVALID_DATA;
        if not isinstance(self.xData[0], (float, int)):
            # is not a spectrum, maybe a batchfile.
            return ERR.INVALID_DATA

        # Data that have same length.
        if len(self.xData) != len(self.yData):
            return ERR.DATA_UNEQUAL_LENGTH;

        # Check file information.
        if not self.timestamp:
            return ERR.INVALID_FILEINFORMATION;

        return ERR.OK;


    def read_file(self, **kwargs)->ERR:

        with open(self.filename, 'r', newline='') as openFile:
            # Set up the reader (even if the file is something else than csv,
            # because we use another dialect then).
            fReader = csv.reader(openFile, dialect=self.subReader.dialect)
            fileinformation = self.subReader.readout_file(fReader, **kwargs)
            self.date, self.time = fileinformation["header"]
            self.data = fileinformation["data"]
            self.parameter = fileinformation.get("parameter", {})
        # return fileinformation


    def read_file_old(self, **kwargs)->ERR:
        """Readout given file"""
        with open(self.filename, 'r', newline='') as openFile:
            # Set up the reader (even if the file is something else than csv,
            # because we use another dialect then).
            fReader = csv.reader(openFile, dialect=self.subReader.dialect)
            data = []
            test = []
            information = set()
            for row in fReader:
                test.append(row)
                lenght = len(row)
                isInformation = (lenght == 1)
                isData = (lenght > 1)
                if isInformation:
                    information.update(row)
                elif isData:
                    data.append(row)

        # Header information
        errorHeader = self.extract_header_n(information, self.subReader)
        if not errorHeader == ERR.OK:
            return errorHeader

        self.data = self.subReader.extract_data(data, **kwargs)
        self.data

        # with open(self.filename, 'r', newline='') as openFile:
        #     # Set up the reader (even if the file is something else than csv,
        #     # because we use another dialect then).
        #     fReader = csv.reader(openFile, dialect=self.subReader.dialect)
        #     # Header information
        #     errorHeader = self.extract_header(fReader, self.subReader)
        #     if errorHeader != ERR.OK:
        #         return errorHeader

        #     # Data
        #     try:
        #         self.data = self.read_data(fReader, self.subReader, **kwargs)
        #         reRead = False
        #     except IndexError:
        #         # self.logger.error(f"Could not read data in {self.filename}!")
        #         # return ERR.INVALID_DATA
        #         reRead = True

        # if reRead:
        #     with open(self.filename, 'r', newline='') as openFile:
        #         fReader = csv.reader(openFile, dialect=self.subReader.dialect)
        #         try:
        #             self.data = self.read_data(fReader, self.subReader, **kwargs)
        #         except IndexError:
        #             self.logger.error(f"Could not read data in {self.filename}!")
        #             return ERR.INVALID_DATA



        return ERR.OK


    def extract_header(self, fReader, subReader):
        """
        Extracts the header information of a file.

        Parameters
        ----------
        fReader : csv.Reader
            The file to read is opened with that reader.
        subReader :

        Returns
        -------
        ERROR_CODE

        """
        marker = self.MARKER["HEADER"]

        for row in fReader:
            try:
                cell = row[0]
            except IndexError:
                # Skip blank rows/lines.
                continue

            if marker in cell:
                self.date, self.time = subReader.get_header(row)
                # Gets the set of parameter of the file if available.
                self.parameter = self.read_parameter(fReader, subReader)
                return ERR.OK;

        self.logger.error(f"No valid header, marker not found '{marker}'")
        return ERR.INVALID_HEADER


    def extract_header_n(self, information:set, subReader):
        marker = self.MARKER["HEADER"]
        markerWildcard = marker + "*"

        headerContainer = fnmatch.filter(information, markerWildcard)
        try:
            self.date, self.time = subReader.get_header(headerContainer)
        except IndexError:
            self.logger.error(f"No valid header, marker not found '{marker}'")
            return ERR.INVALID_HEADER

        parameterContainer = information.copy()
        parameterContainer.difference_update(headerContainer)
        self.parameter = self.read_parameter_n(subReader, parameterContainer)

        return ERR.OK



    def read_data(self, fReader, subReader, **kwargs)->list:
        """
        Read the data of the specified columns of a file opened with a reader.

        Iter through the rows of a file and extracts its data with respect to
        the specified columns.

        Parameters
        ----------
        fReader : csv.Reader
            The file to read is opened with that reader.
        xColumn : int
            The index of the column which contains the x values of the data.
        yColumn : int
            The index of the column which contains the y values of the data.

        Returns
        -------
        data : list
            Contains the x- and y-data. First entry in each element is the x-
            value, second is the y-value.

        """
        data = []
        subReader.preprocess(fReader, **kwargs)
        xColumn, yColumn = subReader.xyColumn
        timeFormat = subReader.subKwargs.get("timeFormat")

        for row in fReader:
            try:
                xData = read_x_data(row[xColumn], timeFormat)
                yData = float(row[yColumn])
                data.append([xData, yData])
            except IndexError:
                break


        return data


    def read_parameter(self, fReader, subReader):
        # TODO: docstring
        parameter = {}
        try:
            parameter = subReader.get_parameter(fReader)
        except AttributeError:
            self.logger.debug("Could not find parameter method.")
        return parameter

    def read_parameter_n(self, subReader, parameterContainer:set):
        parameter = {}
        try:
            parameter = subReader.get_parameter_n(parameterContainer)
        except AttributeError:
            self.logger.debug("Could not find parameter method.")
        return parameter


### Module-level methods

def read_x_data(value:str, timeFormat:datetime=None):
    # TODO: docstring
    try:
        xValue = float(value)
    except ValueError:
        # batch analysis uses timestamp of files for plotting.
        xValue = uni.timestamp_from_string(value, timeFormat)
    return xValue


def is_data(value:str, timeFormat:datetime=None):
    try:
        xValue = float(value)
        return xValue
    except ValueError:
        pass

    # batch analysis uses timestamp of files for plotting.
    try:
        xValue = uni.timestamp_from_string(value, timeFormat)
        return xValue
    except ValueError:
        pass