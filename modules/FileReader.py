#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File Reader module

Import XY data from different filetypes

@author: Hauke Wernecke
"""

# standard libs
import csv
import numpy as np
from datetime import datetime

# third-party libs
from PyQt5.QtCore import QFileInfo  # provides system-independent file info

# local modules/libs
from ConfigLoader import ConfigLoader
from modules.FileFramework import FileFramework


# Load the configuration for extracting data of a data structure.
config = ConfigLoader()
DATA_STRUCTURE = config.DATA_STRUCTURE;


class FileReader(FileFramework):
    """File reader for spectral data files """

    ### Properties

    @property
    def timestamp(self):
        """timestamp getter"""
        strTime = self.date + " " + self.time
        return datetime.strptime(strTime, self.EXPORT["FORMAT_TIMESTAMP"])

    @property
    def data(self):
        """data getter"""
        return (self.xData, self.yData)

    @property
    def header(self):
        """header getter"""
        return (self.filename, self.date, self.time)

    def __init__(self, filename):
        FileFramework.__init__(self, filename)
        self.xData = np.zeros(0)
        self.yData = np.zeros(0)
        self.date = ""
        self.time = ""

        self.__post_init__()


    def __post_init__(self):
        self.read_file()


    def __repr__(self):
        info = {}
        info["Header"] = self.header
        info["Timestamp"] = self.timestamp
        info["data length"] = "X:{}, Y:{}".format(len(self.data[0]),
                                                  len(self.data[1]))
        return self.__module__ + ":\n" + str(info)


    def is_valid_datafile(self) -> bool:
        """
        Checks whether the file contains valid data.

        Returns
        -------
        isValid: bool
            True: Contains valid data.
            False: If not...

        """
        isValid = True;

        # Filetype.
        if not self.get_filetype():
            isValid = False;

        # Data in general.
        if not len(self.xData):
            isValid = False;

        # Data that have same length.
        if len(self.xData) != len(self.yData):
            isValid = False;

        # Check file information.
        if not self.time or not self.date:
            isValid = False;

        return isValid;


    def get_filetype(self):
        """Determine filetype."""
        # Use active dict access here to raise an error.
        suffixes = self.IMPORT["VALID_SUFFIX"]
        fileinfo = QFileInfo(self.filename).suffix().lower()

        if not fileinfo in suffixes:
            fileinfo = False;

        return fileinfo

    def read_file(self):
        """Readout given file"""
        # TODO: config? parentclass?
        # TODO: issue if file has no header
        # TODO: issue if there were no data
        # TODO: issue if file starts with empty line

        # determine the filetype of the file to
        filetype = self.get_filetype()
        if filetype == "csv":
            # csv routine
            get_header = self.get_exported_header
            get_data = self.get_csv_data
        elif filetype == "spk":
            # spk routine
            get_header = self.get_exported_header
            get_data = self.get_spk_data
        elif filetype == "asc":
            get_header = self.get_asc_header
            get_data = self.get_asc_data
        else:
            # TODO: LOG as ERROR?
            print(filetype)
            return 3

        # Get Data from tab separated ascii file
        with open(self.filename, 'r', newline='') as csvFile:
            csvReader = csv.reader(csvFile, dialect=self.dialect)

            if get_header(csvReader, self.MARKER["HEADER"]):
                print("FileReader: No valid header")
                return 1

            data = get_data(csvReader)
            if not len(data):
                print("FileReader: No valid data in ", self.filename)
                return 2

        data = np.array(data)
        self.xData, self.yData = data[:, 0], data[:, 1]
        return 0

    def get_exported_header(self, csvReader, marker):
        """
        Iter through the file opened and accessed with the csvReader to find
        the marker and extract the date and time information to save it to the
        file object

        Parameters
        ----------
        csvReader : csv.reader-object
            Object with opened csv-file.
        marker : string
            marks the date+time row.

        Raises
        ------
        TypeError
            Raises if marker is no string.

        Returns
        -------
        int
            0: Header found and date and time extracted.
            1: Marker not found in Header

        """
        # Set to default to prevent mixing properties of different files.
        self.date = ""
        self.time = ""

        # check the marker
        if type(marker) not in [str]:
            raise TypeError("Marker must be a string");

        # 1. Wrong file format if csvReader reads an empty row
        for row in csvReader:
            if marker in row[0]:
                _, self.date, self.time = row[0].split()
                return 0;

        return 1

    def get_asc_header(self, csvReader, marker):
        """
        Iter through the file opened and accessed with the csvReader to find
        the marker and extract the date and time information to save it to the
        file object

        Parameters
        ----------
        csvReader : csv.reader-object
            Object with opened csv-file.
        marker : string
            marks the date+time row.

        Raises
        ------
        TypeError
            Raises if marker is no string.

        Returns
        -------
        int
            0: Header found and date and time extracted.
            1: Marker not found in Header

        """
        # Set to default to prevent mixing properties of different files.
        self.date = ""
        self.time = ""

        # check the marker
        if type(marker) not in [str]:
            raise TypeError("Marker must be a string");

        # 1. Wrong file format if csvReader reads an empty row.

        for row in csvReader:
            if marker in row[0]:
                _, timestamp = row[0].split(":", 1)
                timestamp = timestamp.strip()

                # Convert the given time string into date and time.
                # TODO: Format to config-file
                dateformat = "%a %b %d %H:%M:%S.%f %Y"
                timestamp = datetime.strptime(timestamp, dateformat)
                # TODO: Format to config-file
                self.date = timestamp.strftime("%d.%m.%Y")
                # TODO: Format to config-file
                self.time = timestamp.strftime("%H:%M:%S")
                return 0;

        return 1

    # TODO: error handlings
    def get_spk_data(self, csvReader):
        """
        Read out the data of a .spk-file respective to its structure.

        Parameters
        ----------
        csvReader : csv.reader-object
            Reader to iterate through the csv-file.

        Returns
        -------
        List of pixel/intensity values

        """
        data = [];

        row = next(csvReader)   #header
        row = next(csvReader)   #units
        for row in csvReader:
            pixel = int(row[0])
            intensity = float(row[DATA_STRUCTURE["SPK_DATA_COLUMN"]])
            data.append([pixel, intensity])

        return data;


    # TODO: error handling
    # TODO: distinguish _raw and _processed?
    def get_csv_data(self, csvReader):
        """
        Read out the data of a .csv-file respective to its structure.

        Parameters
        ----------
        csvReader : csv.reader-object
            Reader to iterate through the csv-file.

        Returns
        -------
        List of pixel/intensity values

        """
        data = [];
        isBatch = False;
        columnXData = 0
        columnYData = DATA_STRUCTURE["CSV_DATA_COLUMN"]

        # iterating until the marker was found
        for row in csvReader:
            if self.MARKER["DATA"] in row[0]:
                break;


        # HACK - Get data of batch file. #####################################
            if "Filename" in row[0]:
                isBatch = True
                break

        if isBatch:
            # get the column of PEAK AREA
            from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHARAC
            try:
                columnYData = row.index(CHARAC.PEAK_AREA.value)
                columnXData = row.index(CHARAC.HEADER_INFO.value)
            except ValueError:
                # May be an issue if one opens the csv file and save it again,
                # that the values are in one line.
                row = row[0].split(",")
                columnYData = row.index(CHARAC.PEAK_AREA.value)
                columnXData = row.index(CHARAC.HEADER_INFO.value)
        # HACK ###############################################################

        # collecting the data
        for row in csvReader:
            try:
                row[columnXData]
            except IndexError:
                # see above as the ValueError in upper try-except.
                row = row[0].split(",")

            if isBatch:
                timestamp = datetime.strptime(row[columnXData],
                                              self.EXPORT["FORMAT_TIMESTAMP"])
                peakArea = float(row[columnYData])
                data.append([timestamp, peakArea])
            else:
                pixel = float(row[columnXData])
                intensity = float(row[columnYData])
                data.append([pixel, intensity])

        return data;


    # TODO: error handling
    def get_asc_data(self, csvReader):
        """
        Read out the data of a .asc-file respective to its structure.

        Parameters
        ----------
        csvReader : csv.reader-object
            Reader to iterate through the asc-file.

        Returns
        -------
        List of pixel/intensity values

        """
        data = [];

        # TODO: Fixed to line 39?
        # TODO: Fixed with 3 blank lines?
        for i in range(37):
            csvReader.__next__()

        # Collecting the data.
        for row in csvReader:
            wavelength = float(row[0])
            intensity = float(row[DATA_STRUCTURE["ASC_DATA_COLUMN"]])
            data.append([wavelength, intensity])

        return data;


