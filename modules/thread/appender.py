#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 16:56:14 2021

@author: hauke
"""

# standard libs

# third-party libs
from PyQt5.QtCore import Signal

# local modules/libs
from modules.thread.worker import Worker
from modules.dataanalysis.spectrumhandler import SpectrumHandler
import modules.dataanalysis.analysis as Analysis
from modules.filehandling.filereading.filereader import FileReader
from modules.filehandling.filewriting.batchwriter import BatchWriter

# type
from c_types.basicsetting import BasicSetting

# exceptions
from exception.InvalidSpectrumError import InvalidSpectrumError



class Appender(Worker):
    signal_valid_file = Signal(str)
    signal_import_batch = Signal(bool)

    def append(self, filename:str, batchFile:str, setting:BasicSetting):
        self._file = FileReader(filename)
        self._batchFile = batchFile
        self._setting = setting
        self.start()

    def run(self):
        if not self._file.is_analyzable():
            return

        try:
            specHandler = SpectrumHandler(self._file, self._setting, useFileWavelength=True)
        except InvalidSpectrumError:
            return

        data, header = Analysis.analyze_file(self._setting, specHandler, self._file)
        BatchWriter(self._batchFile).extend_data(data, header)
        self.signal_valid_file.emit(self._file.filename)
        self.signal_import_batch.emit(True)
