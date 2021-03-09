#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 15:03:07 2021

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

import time

class Exporter(Worker):
    progressChanged = Signal(float)
    skippedFilesTriggered = Signal(list)

    def export(self, files:list, batchFile:str, setting:BasicSetting):
        self._files = files
        self._batchFile = batchFile
        self._setting = setting
        self.start()

    def run(self):
        data = []
        header = []
        skippedFiles = []

        amount = len(self._files)

        before = time.perf_counter()
        for i, file in enumerate(self._files):
            if self.cancel:
                break
            self.progressChanged.emit((i+1)/amount)

            try:
                self.currentFile = FileReader(file)
            except FileNotFoundError:
                skippedFiles.append(file)
                continue

            if not self.currentFile.is_analyzable():
                skippedFiles.append(file)
                continue

            try:
                specHandler = SpectrumHandler(self.currentFile, self._setting, useFileWavelength=True)
            except InvalidSpectrumError:
                skippedFiles.append(file)
                continue

            fileData, header = Analysis.analyze_file(self._setting, specHandler, self.currentFile)
            data.extend(fileData)

        BatchWriter(self._batchFile).export(data, header)
        after = time.perf_counter()
        print("Elapsed time:", after-before)

        self.skippedFilesTriggered.emit(skippedFiles)
