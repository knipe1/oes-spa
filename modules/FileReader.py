#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File Reader module

Import XY data from different filetypes

@author: Hauke Wernecke
"""

# standard libs
import csv
import numpy as np

# third-party libs
from PyQt5.QtCore import QFileInfo  # provides system-independent file info

# local modules/libs
import modules.Universal as uni
from modules.FileFramework import FileFramework


config = uni.load_config()
# marker
MARKER = config["MARKER"];
# export/save
EXPORT = config["EXPORT"];
# file strucutre
DATA_STRUCTURE = config["DATA_STRUCTURE"];


class FileReader(FileFramework):
    """File reader for spectral data files """
    def __init__(self, filename):
        FileFramework.__init__(self)
        self.file = filename
        self.xData = np.zeros(0)
        self.yData = np.zeros(0)
        self.date = ""
        self.time = ""

    def get_filetype(self):
        """Determine filetype"""
        suffixes = ("spk", "Spk", "csv") # TODO: magic
        fileinfo = QFileInfo(self.file).suffix().lower()

        if not fileinfo in suffixes:
            return ""

        return fileinfo

    def read_file(self):
        """Readout given file"""
        # TODO: config? parentclass?
        # TODO: issue if file has no header
        # TODO: issue if there were no data
        # TODO: issue if file starts with empty line
        DEFAULT_TYPE = np.float64


        # Get Data from tab separated ascii file
        with open(self.file, 'r', newline='') as csvFile:
            csvReader = csv.reader(csvFile, dialect=self.dialect)

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
                # asc routine
                pass
            else:
                # TODO: LOG as ERROR?
                print(filetype)
                return 1


            if get_header(csvReader, MARKER["HEADER"]):
                print("FileReader: No valid header")
                return 1
            
            data = get_data(csvReader)
            if not len(data):
                print("FileReader: No valid data")
                return 2

        data = np.array(data, dtype=DEFAULT_TYPE)
        self.xData, self.yData = data[:, 0], data[:, 1]

    def get_values(self):
        """Return x and y data of the file"""
        if not self.xData.size or not self.yData.size:
            self.read_file()
        return self.xData, self.yData

    def get_head(self):
        """Return header information"""
        if not self.time or not self.date:
            self.read_file()
        return self.time, self.date

    def get_exported_header(self, csvReader, marker):
        """
        Iter through the file opened and accessed with the csvReader to find the marker and extract the date and time information to save it to the file object

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
        # set to default to prevent combining properties of different files
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

        # iterating until the marker was found
        for row in csvReader:
            if MARKER["DATA"] in row[0]:
                break;

        # collecting the data
        for row in csvReader:
            pixel = float(row[0])
            intensity = float(row[DATA_STRUCTURE["CSV_DATA_COLUMN"]])
            data.append([pixel, intensity])

        return data;


