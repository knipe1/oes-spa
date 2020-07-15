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
from datetime import datetime

# third-party libs
from PyQt5.QtCore import QFileInfo
from modules.FileFramework import FileFramework

# local modules/libs
import dialog_messages as dialog
import modules.Universal as uni

# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE


class FileWriter(FileFramework):
    """File reader for spectral data files """


    def __init__(self, filename, timestamp=None):
        FileFramework.__init__(self, filename)

        # TODO: Errorhandling if directory is cancelled or does not exist
        # self.directory = self.select_directory()

        # (Create and) assign timestamp.
        if timestamp == None:
            timestamp = datetime.now()
            timestamp = uni.timestamp_to_string(timestamp)
        self.timestamp = timestamp

    def __repr__(self):
        info = {}
        info["filename"] = self.filename
        info["Timestamp"] = self.timestamp
        return self.__module__ + ":\n" + str(info)


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
        exportType : enum EXPORT_TYPE
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
            if exportType in (EXPORT_TYPE.RAW, EXPORT_TYPE.PROCESSED):
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

        # Check whether the user is about to export an exported spectrum.
        isRawSpectrum = rawFilename.rfind(self.EXPORT["RAW_APPENDIX"]) >= 0
        isProccessedSpectrum = rawFilename.rfind(
            self.EXPORT["PROCESSED_APPENDIX"]) >= 0
        if isRawSpectrum or isProccessedSpectrum:
            return ""

        # get the correct appendix
        appendix = ""
        if exportType == EXPORT_TYPE.RAW:
            appendix = self.EXPORT["RAW_APPENDIX"]
        elif exportType == EXPORT_TYPE.PROCESSED:
            appendix = self.EXPORT["PROCESSED_APPENDIX"];

        return rawFilename+appendix+self.EXPORT["EXP_SUFFIX"];

    def build_head(self):
        timestamp = self.timestamp
        try:
            timestamp = uni.timestamp_to_string(timestamp)
        except TypeError:
            # TODO: Implement logger?
            print("Timestamp is no date object.")
        return " ".join([self.MARKER["HEADER"], timestamp])

