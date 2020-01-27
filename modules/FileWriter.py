# -*- coding: utf-8 -*-
"""
File Writermodule

Export raw-/processed spectra

Created on Mon Jan 27 11:02:13 2020
"""
import csv

# QFileInfo provides system-independent file information
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QFileDialog

# parameters
RAW_APPENDIX = "_raw"
PROCESSED_APPENDIX = "_processed"

class FileWriter:
    """File reader for spectral data files """
    def __init__(self, parent, filename):
        self.parent = parent
        csv.register_dialect("spectral_data", delimiter='\t', 
                             quoting=csv.QUOTE_MINIMAL)
        
        self.filename = self.select_file(filename)
        
        
        
    def write_data(self, xyData):
        """"""
        # TODO: backwards compatibility?
        # TODO: compare: with open() as expFile:
        with open(self.filename, 'w', newline='') as expFile:
            csvWr = csv.writer(expFile, dialect="spectral_data")
            csvWr.writerow(["Data of:", self.parent.window.EdFilename.text()])
            csvWr.writerow(["Pixel", "Intensity"])
            csvWr.writerows(xyData)
    
    def select_file(self, filename=""):
        # open a dialog to set the filename if not given
        if not filename:
            filename = QFileDialog.getExistingDirectory(self.parent.widget,
                                   'Save spectrum to...', self.parent.lastdir)
            
        # back up the used directory
        # tODO: which type return absolute path?
        self.parent.lastdir = str(QFileInfo(filename).absolutePath())
        
        # only .csv is allowed
        if QFileInfo(filename).suffix() != "csv":		#magic
            raise TypeError("Only .csv format is allowed!")
        return filename

                    