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
from modules.thread.Worker import Worker
from modules.dataanalysis.SpectrumHandler import SpectrumHandler
import modules.dataanalysis.Analysis as Analysis
from modules.filehandling.filereading.FileReader import FileReader
from modules.filehandling.filewriting.BatchWriter import BatchWriter

# type
from c_types.BasicSetting import BasicSetting

# exceptions
from exception.InvalidSpectrumError import InvalidSpectrumError



class Exporter(Worker):
    signal_exportFinished = Signal(bool)
    signal_progress = Signal(float)
    signal_skipped_files = Signal(list)

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

        for i, file in enumerate(self._files):
            if self.cancel:
                break
            self.signal_progress.emit((i+1)/amount)

            try:
                self.currentFile = FileReader(file)
            except FileNotFoundError:
                skippedFiles.append(file)
                continue

            if not self.currentFile.is_analyzable():
                skippedFiles.append(file)
                continue





            try:
                specHandler = SpectrumHandler(self.currentFile, self._setting, useWLofFile=True)
            except InvalidSpectrumError:
                skippedFiles.append(file)
                continue

            fileData, header = Analysis.analyze_file(self._setting, specHandler, self.currentFile)
            data.extend(fileData)

        BatchWriter(self._batchFile).export(data, header)

        self.signal_skipped_files.emit(skippedFiles)
