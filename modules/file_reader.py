#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File Reader module

Import XY data from different filetypes
"""
import numpy as np
from PyQt5.QtCore import QFileInfo


class FileReader:
    """File reader for spectral data files """
    def __init__(self, filename):
        self.filetype = ""
        self.file = filename
        self.xData = np.array([0])
        self.yData = np.array([0])
        self.date = ""
        self.time = ""

    def get_filetype(self):
        """Determine filetype"""
        fileinfo = str(QFileInfo(self.file).suffix())
        if fileinfo == "Spk" or fileinfo == "spk":
            self.filetype = "SpexHex"
            return 0
        return 1

    def read_file(self):
        """Readout given file"""

        if self.filetype == "SpexHex":
            # Get Data from tab separated ascii file
            import csv
            csvreader = csv.reader(open(self.file, 'r'), delimiter='\t',
                                   quoting=csv.QUOTE_NONE)
            x_data = []
            y_data = []
            getdata = False
            for row in csvreader:
                if getdata:
                    x_data.append(float(row[0].replace(',', '.')))
                    y_data.append(float(row[3].replace(',', '.')))
                elif row:
                    if "Date" in row[0]:
                        sep = row[0].split()
                        self.date = sep[1]
                        self.time = sep[2]
                    if len(row) > 1 and len(row[0]) == 0:
                        getdata = True

            self.xData = np.array(x_data)
            self.yData = np.array(y_data)

    def get_values(self):
        """return x and y data of the file"""
        if self.filetype == "":
            if not self.get_filetype():
                self.read_file()
        return self.xData, self.yData
