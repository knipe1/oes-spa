#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 09:39:36 2020

@author: Hauke Wernecke
"""

# standard libs
from os import path
from datetime import datetime

# third-party libs

# local modules/libs
# FileWriter: base class.
from modules.filehandling.filewriting.filewriter import FileWriter
import modules.universal as uni
from modules.dataanalysis.spectrum import Spectrum

# Enums
from c_enum.EXPORT_TYPE import EXPORT_TYPE
from c_enum.SUFFICES import SUFFICES as SUFF

# constants
PROCESSED_APPENDIX = "_processed"
RAW_APPENDIX = "_raw"
EXPORT_SUFFIX = SUFF.CSV


class SpectrumWriter(FileWriter):

    def __init__(self, filename:str, timestamp:datetime):
        filename = uni.replace_suffix(filename, suffix=EXPORT_SUFFIX)
        super().__init__(filename, timestamp)


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
            return None

        exportFilename = self.assemble_export_filename(spectrum.exportType)

        data = spectrum.data
        columnTitles = spectrum.labels.values()
        super().export(exportFilename, data, columnTitles, extraInformation)

        return exportFilename


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
