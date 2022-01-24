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
from PyQt5.QtWidgets import QWidget

import modules.universal as uni
from ui.Uimultibatch import UIMultiBatch
import dialog_messages as dialog
from .filehandling.filereading.bareader import BaReader
from ui.multibatch_canvas import Multibatch_Canvas


# enums and dataclasses
from c_enum.suffices import SUFFICES as SUFF
from c_enum.multi_batch_setting import MultiBatchSetting

# constants
BATCH_SUFFIX = SUFF.BATCH


# exceptions
from exception.InvalidBatchFileError import InvalidBatchFileError

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
        # Canvas
        self._traceSpectrum = Multibatch_Canvas(self._window.mplBatch)
        # signals
        self.batchfileChanged.connect(self._window.set_batchfilename)
        self.batchfileAdded.connect(self._window.insert_batchfile)
        self.analysisAdded.connect(self._window.add_analysis)
        self._window.connect_import_batchfile(self._specify_batchfile)
        self._window.connect_add_batchfile(self.append_batchfile)
        self._window.connect_tree_settings_changed(self.plot_trace_from_batchfile)


    def _specify_batchfile(self)->None:
        """Specifies the filename through a dialog."""
        filename = dialog.dialog_importBatchfile()
        self.batchFile = filename


    def append_batchfile(self):
        self._logger.info(f"Append Batchfile: {self.batchFile}")
        if self.batchFile and self.batchFile not in self._window.get_batch_filenames():
            self.batchfileAdded.emit(self.batchFile)
        self.analysisAdded.emit(self.batchFile)


    def plot_trace_from_batchfile(self, settings:MultiBatchSetting)->None:
        data = []
        for batchfile, settings in settings.items():
            try:
                batch = BaReader(filename=batchfile)
            except (FileNotFoundError, InvalidBatchFileError):
                continue

            for s in settings:
                timestamps, values = batch.get_data(s.peakname, s.characteristic)
                timeaxis = uni.convert_to_hours(timestamps - timestamps[0]) + s.xoffset
                values += s.yoffset
                traceData = np.array((timeaxis, values))
                label = self._setting_to_label(s)
                data.append((traceData, label))


        self._traceSpectrum.plot(data)


    def _setting_to_label(self, s:dict):
        label = f"{s.peakname} - {s.characteristic} - X: {s.xoffset} - Y: {s.yoffset}"
        return label