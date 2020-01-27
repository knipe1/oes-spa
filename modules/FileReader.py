#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File Reader module

Import XY data from different filetypes
"""
import csv

import numpy as np
# QFileInfo provides system-independent file information
from PyQt5.QtCore import QFileInfo
                                            

class FileReader:
    """File reader for spectral data files """
    def __init__(self, filename):
        print(filename) # is the path+filename
        self.filetype = ""
        self.file = filename
        self.xData = np.zeros(0)
        self.yData = np.zeros(0)
        self.date = ""
        self.time = ""

    def get_filetype(self):
        """Determine filetype"""
        suffixes = ("spk", "Spk", "csv")
        fileinfo = QFileInfo(self.file).suffix()
        if fileinfo in suffixes:
            return 0
        return 1

    def read_file(self):
        """Readout given file"""
        DEFAULT_TYPE = np.float64
        DELIMITER = "\t"
        HEADER_MARKER = "Date"
        DATA_MARKER = "Data"
        
        # declaration
        x_data = []
        y_data = []
        #getdata = False

        if not self.get_filetype():
            # Get Data from tab separated ascii file
            with open(self.file, 'r') as csvFile:
                csvReader = csv.reader(csvFile, delimiter=DELIMITER, 
                                       quoting=csv.QUOTE_NONE)
                
                row = next(csvReader)
                self.read_head(row[0], HEADER_MARKER)
                row = next(csvReader)   #header
                row = next(csvReader)   #units
                test = 3
                if self.file.find(".csv") >= 0:
                    test = 1
                    
                for row in csvReader:
                    # TODO: is there any value with a commata?
                    x_data.append(row[0].replace(',', '.')) # TODO: magic
                    y_data.append(row[test].replace(',', '.')) # TODO: magic

            self.xData = np.array(x_data, dtype=DEFAULT_TYPE)
            self.yData = np.array(y_data, dtype=DEFAULT_TYPE)

    def get_values(self):
        """Return x and y data of the file"""
        if not self.get_filetype():
            self.read_file()
        return self.xData, self.yData

    def get_head(self):
        """Return header information"""
        if not self.get_filetype():
            self.read_file()
        return self.time, self.date
        
        '''if self.filetype == "":
            if not self.get_filetype():
                self.read_file()
        elif self.filetype == "SpexHex":
            return self.time, self.date

        return 0, 0'''
    
    def read_head(self, data, marker):
        """read the date and time, 
        if the marker is in the first element of the data
        return: 0 if header was found, else 1"""
        if not marker in data:
            return 1
        
        sep = data.split()
        self.date = sep[1]
        self.time = sep[2]
        return 0
        
                
