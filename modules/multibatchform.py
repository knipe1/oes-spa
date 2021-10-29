#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 11:46:07 2021

@author: Hauke Wernecke
"""


# standard libs
import logging
import numpy as np

# third-party libs
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QWidget

import modules.universal as uni
from ui.Uimultibatch import UIMultiBatch
import dialog_messages as dialog
from modules.filehandling.filereading.filereader import FileReader
from .dataanalysis.trace import Trace

from c_enum.suffices import SUFFICES as SUFF


# constants
BATCH_SUFFIX = SUFF.BATCH


class MultiBatchForm(QWidget):

    ### Signals
    batchfileChanged = pyqtSignal(str)
    batchfileAdded = pyqtSignal(str)
    analysisAdded = pyqtSignal(str)

    ### Properties

    @property
    def batchFile(self)->str:
        return self._batchFile

    @batchFile.setter
    def batchFile(self, filename:str)->None:
        """batchFile setter: Updating the ui"""
        if filename == "":
            return

        if filename is not None:
            filename = uni.replace_suffix(filename, suffix=BATCH_SUFFIX)
        else:
            filename = ""
        self._batchFile = filename
        self.batchfileChanged.emit(filename)


    def __init__(self, parent)->None:
        """
        Parameters
        ----------
        parent : AnalysisWindow
            Required for the interplay between the two windows.

        """
        super().__init__(parent)
        self._logger = logging.getLogger(self.__class__.__name__)

        self._batchFile = None

        # Set up ui.
        self._window = UIMultiBatch(parent)

        self.__post_init__()


    def __post_init__(self):

        self._traceSpectrum = Trace(self._window.mplBatch)
        # signals
        self.batchfileChanged.connect(self._window.set_batchfilename)
        self.batchfileAdded.connect(self._window.insert_batchfile)
        self.analysisAdded.connect(self._window.add_analysis)
        self._window.connect_import_batchfile(self._specify_batchfile)
        self._window.connect_add_batchfile(self.append_batchfile)


    def _specify_batchfile(self)->None:
        """Specifies the filename through a dialog."""
        filename = dialog.dialog_importBatchfile()
        self.batchFile = filename


    def append_batchfile(self):
        self._logger.info(f"Append Batchfile: {self.batchFile}")
        if not self.batchFile in self._window.get_batch_filenames():
            self.batchfileAdded.emit(self.batchFile)
        self.analysisAdded.emit(self.batchFile)



    def plot_trace_from_batchfile(self, filename:str, characteristic:str, peakname:str, )->None:
        # TODO: Add x and y offset
        try:
            file = FileReader(filename, columnValue=characteristic)
        except FileNotFoundError:
            return

        if not file.is_valid_batchfile():
            return

        # TODO: See #98
        self._traceSpectrum.reset_time()
        timestamps, values = zip(*file.data[peakname])
        diffTimes = self._traceSpectrum.calculate_time_differences(timestamps)
        traceData = np.array((diffTimes, values)).transpose()
        file.data[peakname] = traceData

        # Plot the trace.
        self._traceSpectrum.set_data(file.data[peakname])
