#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Writermodule

Export raw-/processed spectra

Created on Mon Jan 27 11:02:13 2020

@author: Hauke Wernecke
"""

# standard libs
import csv

# third-party libs
from PyQt5.QtCore import QFileInfo
from modules.FileFramework import FileFramework

# local modules/libs
import dialog_messages as dialog
from modules.Universal import ExportType


class FileWriter(FileFramework):
    """File reader for spectral data files """
    def __init__(self, parent, filename, timestamp):
        FileFramework.__init__(self, filename)
        # TODO: doublecheck usage of parent...
        self.parent = parent

        # TODO: Errorhandling if directory is cancelled or does not exist
        # self.directory = self.select_directory()
        self.timestamp = timestamp




    def write_data(self, data, labels, exportType, additionalInformation = {}):
        """
        Writes the header, additional information, label and data into a csv file.

        Parameters
        ----------
        data : List or tuple
            List or tuple of x- and y-data. Does not take the values itself into account, so it do not matter whether these data is pixel, intensity or wavelength
        labels : list of strings
            Describes the properties of the data.
        additionalInformation : dict, optional
            A dictionary that uses the Key and value as entries. Used for additional characteristic values. The default is {}.
        exportType : enum ExportType
            Adding an appendix to the filename according to the spectrum that is exported.

        Returns
        -------
        bool
            True: if exported.
            False: if directory is not set.

        """
        expFilename = self.build_exp_filename(exportType)
        if not expFilename:
            return False

        with open(expFilename, 'w', newline='') as expFile:
            # open writer with self defined dialect
            csvWr = csv.writer(expFile, dialect=self.dialect)
            # creating the head using file specific properties
            csvWr.writerow([self.build_head()])
            # adding characteristic values
            for key, value in additionalInformation.items():
                csvWr.writerow([key, value])
            # adding labels
            csvWr.writerow(labels)
            # adding marker. Important also for import function
            if exportType == ExportType.RAW or exportType == ExportType.PROCESSED:
                csvWr.writerow([self.MARKER["DATA"]])
            # write data
            csvWr.writerows(data)

        dialog.information_ExportFinished(expFilename)
        return True


    def build_exp_filename(self, exportType):
        """Alters the current filename to a standard processed export
        filename"""
        rawFilename = self.filename
        # remove the suffix
        # TODO: doublecheck methods
        for suffix in self.IMPORT["VALID_SUFFIX"]:
            rawFilename = rawFilename.replace("."+suffix, "")

        # check whether the user is about to export an exported spectrum
        if rawFilename.rfind(self.EXPORT["RAW_APPENDIX"]) >= 0\
            or rawFilename.rfind(self.EXPORT["PROCESSED_APPENDIX"]) >= 0\
            or rawFilename.rfind(self.EXPORT["DEF_BATCH_NAME"]) >= 0:
                return ""

        # get the correct appendix
        appendix = ""
        if exportType == ExportType.RAW:
            appendix = self.EXPORT["RAW_APPENDIX"]
        elif exportType == ExportType.PROCESSED:
            appendix = self.EXPORT["PROCESSED_APPENDIX"];

        return rawFilename+appendix+self.EXPORT["EXP_SUFFIX"];

    def build_head(self):
        return " ".join([self.MARKER["HEADER"], self.timestamp])

