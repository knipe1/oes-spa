# -*- coding: utf-8 -*-
"""
File Writermodule

Export raw-/processed spectra

Created on Mon Jan 27 11:02:13 2020
"""
import csv

# from PyQt5.QtWidgets import QFileDialog

from modules.FileFramework import FileFramework

import dialog_messages as dialog


class FileWriter(FileFramework):
    """File reader for spectral data files """
    def __init__(self, parent, filename, date, time):
        FileFramework.__init__(self)
        self.parent = parent

        self.directory = self.select_directory()
        self.filename, self.date, self.time = filename, date, time



    def write_data(self, xyData, xLabel, yLabel, additionalInformation = {},
                   isRaw=False):
        """"""
        if not self.directory:
            return 1

        expFilename = self.build_exp_filename(isRaw)
        # TODO: sense of newline=''?
        with open(expFilename, 'w', newline='') as expFile:
            # open writer with self defined dialect
            csvWr = csv.writer(expFile, dialect=self.dialect)
            csvWr.writerow([self.build_head()])
            for key, value in additionalInformation.items():
                csvWr.writerow([key, value])
            csvWr.writerow([xLabel, yLabel])
            csvWr.writerow([self.MARKER["DATA"]])
            csvWr.writerows(xyData)
        return 0

    def select_directory(self):
        # open a dialog to set the filename if not given
        # saveMessage = 'Save spectrum to...'
        # directory = QFileDialog.getExistingDirectory(self.parent.widget,
        #                            caption=saveMessage,
        #                            directory=self.parent.lastdir)
        dialog.dialog_getDirectory(self.parent.lastdir, self.parent.widget)
        # back up the used directory, if a directory was selected
        if directory:
            self.parent.lastdir = directory
        return directory

    def build_exp_filename(self, isRaw=False):
        """Alters the current filename to a standard processed export
        filename"""
        rawFilename = self.filename
        # remove the suffix
        for suffix in self.LOAD["VALID_SUFFIX"]:
            rawFilename = rawFilename.replace("."+suffix, "")
        # get the correct appendix
        appendix = self.SAVE["PROCESSED_APPENDIX"];
        if isRaw:
            appendix = self.SAVE["RAW_APPENDIX"]
        return rawFilename+appendix+self.SAVE["EXP_SUFFIX"];

    def build_head(self):
        return " ".join([self.MARKER["HEADER"], self.date, self.time])

