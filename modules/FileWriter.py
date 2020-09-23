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
from os import path
from datetime import datetime

# third-party libs
from PyQt5.QtCore import QFileInfo

# local modules/libs
from modules.FileFramework import FileFramework
import dialog_messages as dialog
import modules.Universal as uni

# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE

# constants
PROCESSED_APPENDIX = "_processed"
RAW_APPENDIX = "_raw"


class FileWriter(FileFramework):
    """File reader for spectral data files """

    def __init__(self, filename, timestamp=None):
        FileFramework.__init__(self, filename)
        self.timestamp = self.determine_timestamp(timestamp)
        self.dialect = self.csvDialect


    def __repr__(self):
        info = {}
        info["filename"] = self.filename
        info["Timestamp"] = self.timestamp
        return self.__module__ + ":\n" + str(info)


    def determine_timestamp(self, timestamp):
        if timestamp == None:
            timestamp = datetime.now()
            timestamp = uni.timestamp_to_string(timestamp)
        return timestamp


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

        expFilename = self.build_exp_filename(self.filename, exportType)
        if not expFilename:
            return False

        with open(expFilename, 'w', newline='') as expFile:
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

    def write_line(self, data):
        # TODO: docstring
        with open(self.filename, 'a', newline='') as f:
            # open writer with self defined dialect
            writer = csv.writer(f, dialect=self.dialect)
            writer.writerow(data)



    def build_exp_filename(self, filename, exportType):
        """Alters the current filename to a standard processed export filename"""
        filepath, baseName = uni.extract_path_and_basename(filename)

        if is_exported_spectrum(baseName):
            return

        appendix = determine_appendix(exportType)

        exportFilename = path.join(filepath, baseName + appendix)
        exportFilename = uni.replace_suffix(exportFilename)

        return exportFilename

    def build_head(self):
        # TODO: docstring
        timestamp = self.timestamp
        try:
            timestamp = uni.timestamp_to_string(timestamp)
        except TypeError:
            # TODO: Implement logger?
            print("Timestamp is no date object.")
        return " ".join([self.MARKER["HEADER"], timestamp])


def is_exported_spectrum(filename):
    isRawSpectrum = (filename.rfind(RAW_APPENDIX) >= 0)
    isProccessedSpectrum = filename.rfind(PROCESSED_APPENDIX) >= 0
    isExported = isRawSpectrum or isProccessedSpectrum
    return isExported


def determine_appendix(exportType):
    appendix = ""
    if exportType == EXPORT_TYPE.RAW:
        appendix = RAW_APPENDIX
    elif exportType == EXPORT_TYPE.PROCESSED:
        appendix = PROCESSED_APPENDIX
    return appendix
