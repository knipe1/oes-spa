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
# FileWriter: base class.
from modules.filehandling.filewriting.FileWriter import FileWriter
import modules.Universal as uni
from modules.dataanalysis.Spectrum import Spectrum

# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE

# constants
PROCESSED_APPENDIX = "_processed"
RAW_APPENDIX = "_raw"


class SpectrumWriter(FileWriter):

    def __init__(self, filename, timestamp):
        super().__init__(filename)
        self.timestamp = timestamp
        self.dialect = self.csvDialect


    def __repr__(self):
        info = {}
        info["filename"] = self.filename
        info["Timestamp"] = self.timestamp
        return self.__module__ + ":\n" + str(info)


    def export(self, spectrum:Spectrum, extraInformation:dict=None)->str:
        """
        Parameters
        ----------
        spectrum : Spectrum
            Information about the spectrum to export.
        extraInformation : dict, optional (default {})
            Used for characteristic values like peak height,...
        """
        if is_exported_spectrum(self.filename):
            return

        exportFilename = self.assemble_export_filename(spectrum.exportType)

        data = spectrum.data
        columnTitles = spectrum.labels.values()
        super().export(exportFilename, data, columnTitles, extraInformation)

        return exportFilename


    def write_data(self, fWriter:csv.writer, data:list)->None:
        fWriter.writerow([self.MARKER["DATA"]])
        fWriter.writerows(data)


    def assemble_export_filename(self, exportType:EXPORT_TYPE)->str:
        """Alters the current filename to a standard processed export filename"""
        appendix = determine_appendix(exportType)

        filepath, baseName, suffix = uni.extract_path_basename_suffix(self.filename)
        exportFilename = path.join(filepath, baseName + appendix + '.' + suffix)
        return exportFilename


def is_exported_spectrum(filename:str)->bool:
    baseName = path.basename(filename)
    isRawSpectrum = (baseName.rfind(RAW_APPENDIX) >= 0)
    isProccessedSpectrum = (baseName.rfind(PROCESSED_APPENDIX) >= 0)
    isExported = (isRawSpectrum or isProccessedSpectrum)
    return isExported


def determine_appendix(exportType:EXPORT_TYPE)->str:
    if exportType == EXPORT_TYPE.RAW:
        appendix = RAW_APPENDIX
    elif exportType == EXPORT_TYPE.PROCESSED:
        appendix = PROCESSED_APPENDIX
    return appendix