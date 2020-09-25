#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 09:39:36 2020

@author: Hauke Wernecke
"""

# standard libs
import csv
from os import path

# third-party libs

# local modules/libs
from modules.FileFramework import FileFramework
import dialog_messages as dialog
import modules.Universal as uni

# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE

# constants
PROCESSED_APPENDIX = "_processed"
RAW_APPENDIX = "_raw"


class SpectrumWriter(FileFramework):


    def __init__(self, filename, timestamp):
        FileFramework.__init__(self, filename)
        self.timestamp = timestamp
        self.dialect = self.csvDialect


    def __repr__(self):
        info = {}
        info["filename"] = self.filename
        info["Timestamp"] = self.timestamp
        return self.__module__ + ":\n" + str(info)


    def export(self, data, titles, exportType, additionalInformation = {}):
        """
        Writes the header, additional information, label and data into a csv file.

        Parameters
        ----------
        data : List or tuple
            List or tuple of x- and y-data. Does not take the values itself into account, so it do not matter whether these data is pixel, intensity or wavelength
        titles : list of strings
            Describes the properties of the data.
        additionalInformation : dict, optional
            A dictionary that uses the Key and value as entries. Used for additional characteristic values. The default is {}.
        exportType : enum EXPORT_TYPE
            Adding an appendix to the filename according to the spectrum that is exported.
        """

        # Note: If the appendices are in the directory name, this is treated like an exported spectrum.
        if is_exported_spectrum(self.filename):
            return

        exportFilename = build_exp_filename(self.filename, exportType)

        with open(exportFilename, 'w', newline='') as exportFile:
            fWriter = csv.writer(exportFile, dialect=self.dialect)
            self.write_header(fWriter)
            self.write_information(fWriter, additionalInformation)
            self.write_column_titles(fWriter, titles)
            self.write_data(fWriter, data)

        dialog.information_ExportFinished(exportFilename)
        return


    def write_header(self, fWriter):
        strTimestamp = uni.timestamp_to_string(self.timestamp)
        header =  self.MARKER["HEADER"] + " " + strTimestamp
        fWriter.writerow([header])


    def write_column_titles(self, fWriter, titles):
        fWriter.writerow(titles)


    def write_information(self, fWriter:csv.writer, information:dict):
        for key, value in information.items():
            fWriter.writerow([key, value])

    def write_data(self, fWriter:csv.writer, data):
        fWriter.writerow([self.MARKER["DATA"]])
        fWriter.writerows(data)


def build_exp_filename(filename, exportType):
    """Alters the current filename to a standard processed export filename"""
    filepath, baseName = uni.extract_path_and_basename(filename)

    appendix = determine_appendix(exportType)

    exportFilename = path.join(filepath, baseName + appendix)
    exportFilename = uni.replace_suffix(exportFilename)

    return exportFilename


def is_exported_spectrum(filename):
    isRawSpectrum = (filename.rfind(RAW_APPENDIX) >= 0)
    isProccessedSpectrum = filename.rfind(PROCESSED_APPENDIX) >= 0
    isExported = (isRawSpectrum or isProccessedSpectrum)
    return isExported


def determine_appendix(exportType):
    appendix = ""
    if exportType == EXPORT_TYPE.RAW:
        appendix = RAW_APPENDIX
    elif exportType == EXPORT_TYPE.PROCESSED:
        appendix = PROCESSED_APPENDIX
    return appendix