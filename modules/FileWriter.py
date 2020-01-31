# -*- coding: utf-8 -*-
"""
File Writermodule

Export raw-/processed spectra

Created on Mon Jan 27 11:02:13 2020
"""
import csv

from PyQt5.QtWidgets import QFileDialog

import modules.Universal as uni


config = uni.load_config()

# parameters
SAVE = config["SAVE"]
LOAD = config["LOAD"]

MARKER = config["MARKER"]

DIALECT = config["DIALECT"]

class FileWriter:
    """File reader for spectral data files """
    def __init__(self, parent, filename, date, time):
        self.parent = parent
        csv.register_dialect(DIALECT["name"], 
                             delimiter = DIALECT["delimiter"], 
                             quoting = DIALECT["quoting"])
        
        self.directory = self.select_directory()
        self.filename, self.date, self.time = filename, date, time
        
        
        
    def write_data(self, xyData, xLabel, yLabel, additionalInformation = {},
                   isRaw=False):
        """"""
        if not self.directory:
            return 1
                
        expFilename = self.build_exp_filename(isRaw)
        with open(expFilename, 'w', newline='') as expFile:
            # open writer with self defined dialect
            csvWr = csv.writer(expFile, dialect=DIALECT["name"])
            csvWr.writerow([" ".join([MARKER["HEADER"], self.date, self.time])])
            for key, value in additionalInformation.items():
                csvWr.writerow([key, value])
            csvWr.writerow([xLabel, yLabel])
            csvWr.writerow([ MARKER["DATA"]])
            csvWr.writerows(xyData)
    
    def select_directory(self):
        # open a dialog to set the filename if not given
        directory = QFileDialog.getExistingDirectory(self.parent.widget,
                                   'Save spectrum to...', self.parent.lastdir)
        if directory:
            # back up the used directory
            self.parent.lastdir = directory
        return directory
    
    def build_exp_filename(self, isRaw=False):
        """"""
        rawFilename = self.filename
        for suffix in LOAD["VALID_SUFFIX"]:
            rawFilename = rawFilename.replace("."+suffix, "")
        appendix = SAVE["PROCESSED_APPENDIX"];
        if isRaw:
            appendix = SAVE["RAW_APPENDIX"]
        return rawFilename+appendix+SAVE["EXP_SUFFIX"];

                    