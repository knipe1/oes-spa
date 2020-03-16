#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File Reader module

Import XY data from different filetypes
"""
# imports
import csv

import numpy as np
from PyQt5.QtCore import QFileInfo  # provides system-independent file info
from PyQt5.QtWidgets import QMessageBox # TODO: remove

import modules.Universal as uni
# classes
from modules.FileFramework import FileFramework


config = uni.load_config()
# marker
MARKER = config["MARKER"];
# export/save
SAVE = config["SAVE"];
# file strucutre
DATA_STRUCTURE = config["DATA_STRUCTURE"];


class FileReader(FileFramework):
    """File reader for spectral data files """
    def __init__(self, filename):
        FileFramework.__init__(self)
        # print(filename) # is the path+filename
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
        DEFAULT_TYPE = np.float64

        # declaration
        x_data = []
        y_data = []


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

            get_header(csvReader, MARKER["HEADER"])
            data = get_data(csvReader)


            # spk-files have a different structure than csv files
            # if self.file.find(SAVE["EXP_SUFFIX"]) >= 0:
            #     dataCol = DATA_STRUCTURE["CSV_DATA_COLUMN"]
            # else:
            #     dataCol = DATA_STRUCTURE["SPK_DATA_COLUMN"]

            # check if it is valid raw spectrum or critical processed spectrum

            # if dataCol == DATA_STRUCTURE["CSV_DATA_COLUMN"] and row[0] != MARKER["DATA"]:
            #     while row[0] != MARKER["DATA"]:
            #         row = next(csvReader)
            #     QMessageBox.warning(None, "Test", "Processed");

            # for row in csvReader:
            #     x_data.append(row[0].replace(',', '.')) # TODO: magic
            #     y_data.append(row[dataCol].replace(',', '.')) # TODO: magic

        # self.xData = np.array(x_data, dtype=DEFAULT_TYPE)
        # self.yData = np.array(y_data, dtype=DEFAULT_TYPE)
        data = np.array(data, dtype=DEFAULT_TYPE)
        print("shape:", data.shape)
        print("type:", type(data))
        self.xData = data[:, 0]
        print("xData:", self.xData)
        self.yData = data[:, 1]

    def get_values(self):
        """Return x and y data of the file"""
        if not self.xData:
            print("Error 1")
            self.read_file()
        return self.xData, self.yData

    def get_head(self):
        """Return header information"""
        if not self.time:
            print("Error 2", self.time)
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
        # 2.
        for row in csvReader:
            if marker in row[0]:
                sep = row[0].split()
                self.date = sep[1]
                self.time = sep[2]
                return 0;

        return 1
        # if not len(data) > 0:
        #     QMessageBox.critical(None, "Wrong Data", "No Data given to read out the Header")
        #     return 2
        # if not marker in data[0]:
        #     QMessageBox.critical(None, "ValueError", "No Header included. Wrong format or wrong file input.")
        #     return 1


        # return 0

    # TODO: doc
    def get_spk_data(self, csvReader):

        data = [];

        row = next(csvReader)   #header
        row = next(csvReader)   #units
        for row in csvReader:
            pixel = int(row[0])
            intensity = float(row[DATA_STRUCTURE["SPK_DATA_COLUMN"]])
            data.append([pixel, intensity])

        return data;

    # TODO: doc
    # TODO: distinguish _raw and _processed?
    def get_csv_data(self, csvReader):

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


