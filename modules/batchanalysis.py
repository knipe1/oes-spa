#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glossary:
    batchfile: The file in which the characteristic values are exported to.

Note:
    When handling paths, absolute paths are used in comparisons.

Created on Mon Jan 20 10:22:44 2020

@author: Hauke Wernecke
"""

# standard libs
from os import path
import logging
import numpy as np

# third-party libs
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QKeySequence as QKeys

# local modules/libs
# UI
from ui.UIbatch import UIBatch
# modules & universal
import modules.universal as uni
import dialog_messages as dialog
from modules.dataanalysis.trace import Trace
from modules.watchdog import Watchdog
from modules.filehandling.filereading.filereader import FileReader
from modules.thread.appender import Appender
from modules.thread.exporter import Exporter
from modules.thread.plotter import Plotter


# Enums
from c_types.fileset import FileSet
from c_types.basicsetting import BasicSetting
from c_enum.suffices import SUFFICES as SUFF


# constants
BATCH_SUFFIX = SUFF.BATCH


class BatchAnalysis(QDialog):
    """
    Provides an dialog widget as interface to analyze multiple spectra.

    Provides a multiple file handling interface.
    May extract characteristic values for further applications.

    Usage:
        from modules.batchanalysis import BatchAnalysis
        batch = BatchAnalysis(parent)  # parent as main window or application

    """

    ### Signals
    batchfileChanged = pyqtSignal(str)
    WDdirectoryChanged = pyqtSignal(str)
    fileSelected = pyqtSignal(FileReader, bool)
    cancelInitiated = pyqtSignal(bool)

    ### Slots

    @pyqtSlot()
    @pyqtSlot(bool)
    def update_batch(self, force:bool=False)->None:
        if self._window.get_plot_trace() or force:
            self.import_batchfile(takeCurrentBatchfile=True)


    @pyqtSlot(list)
    def handle_skipped_files(self, skippedFiles:list)->None:
        dialog.information_batchAnalysisFinished(skippedFiles)
        self._files.difference_update(skippedFiles)


    @pyqtSlot(str)
    def add_file(self, filename:str)->None:
        self._files.update([filename], noSelection=True)


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



    ### __methods__

    def __init__(self, parent)->None:
        """
        Parameters
        ----------
        parent : AnalysisWindow
            Required for the interplay between the two windows.

        """
        # Initialize the parent class [equivalent to: QDialog.__init__(self)].
        super().__init__(parent)

        self._logger = logging.getLogger(self.__class__.__name__)

        # Init the props to prevent errors in the ui-init routine.
        # (SystemError: <built-in function connectSlotsByName> returned a result with an error set)
        self._batchFile = None
        self._thread = None
        self.currentFile = None
        self.setting = None

        # Set up ui.
        self._window = UIBatch(self)

        self.__post_init__()


    def __post_init__(self)->None:
        self._files = FileSet(listWidget=self._window.listFiles)
        self._dog = Watchdog(self._spectrum_modified_handler)
        self._traceSpectrum = Trace(self._window.plotTraceSpectrum)

        # Link events of the ui to methods of this class.
        self._set_connections()


    def __repr__(self)->str:
        info = {}
        info["batchfile"] = self.batchFile
        info["files"] = self._files
        return self.__module__ + ":\n" + str(info)


    ### methods

    def _set_connections(self)->None:
        """Set Signal-Slot connections."""
        # buttons
        self._window.connect_analyze(self.analyze)
        self._window.connect_browse_spectra(self._browse_spectra)
        self._window.connect_cancel(self.schedule_cancel_routine)
        self._window.connect_reset(self.reset_batch)
        self._window.connect_import_batchfile(self.import_batchfile)
        self._window.connect_refresh(self.import_batchfile)
        self._window.connect_set_batchfile(self._specify_batchfile)
        self._window.connect_set_watchdog_directory(self._specify_watchdog_directory)
        self._window.connect_watchdog(self._trigger_watchdog)
        # change events
        self._window.connect_change_trace(self.import_batchfile)
        self._window.connect_select_file(self.open_indexed_file)
        # signals
        self.batchfileChanged.connect(self._window.set_batchfilename)
        self.WDdirectoryChanged.connect(self._window.set_WDdirectory)
        self.WDdirectoryChanged.connect(self._dog.set_directory)
        self._dog.dog_alive.connect(self._window.enable_WD)
        self.fileSelected.connect(self.parent().plot_spectrum)


    ### Events

    def closeEvent(self, event)->None:
        """Closing the BatchAnalysis dialog to have a clear shutdown."""
        event.accept()
        self.schedule_cancel_routine()
        self._dog.trigger_status(False)


    def keyPressEvent(self, event)->None:
        """
        Key handling.

        Regarding deletions, cancellations,...
        """
        event.accept()

        # Cancel current analysis.
        isCancel = event.matches(QKeys.Cancel)
        if isCancel:
            self.schedule_cancel_routine()
            return

        # Remove currently selected file.
        isFocused = self._window.is_focussed_filelist()
        isDelete = event.matches(QKeys.Delete)
        if isFocused and isDelete:
            row = self._files.current_row
            self._files.remove(self._files[row])
            return


    @staticmethod
    def dragEnterEvent(event)->None:
        """Note: Validation takes place in dropEvent-handler."""
        event.accept()


    def dropEvent(self, event)->None:
        """Filter the dropped urls to update the files with only valid urls."""
        urls = event.mimeData().urls()
        localUrls = [uni.get_valid_local_url(url) for url in urls]
        localUrls = self._drop_invalid_urls(localUrls)
        self.update_filelist(localUrls)


    def _drop_invalid_urls(self, urls:list)->set:
        validUrls = set(urls)
        try:
            validUrls.remove(None)
            dialog.critical_unknownSuffix(parent=self)
        except KeyError:
            self._logger.info("No invalid url found.")

        return validUrls


    ### Watchdog routines

    def _spectrum_modified_handler(self, pathname:str)->None:
        self._logger.info("Spectrum file modified/added: %s", pathname)
        self.analyze_single_file(pathname)


    def _trigger_watchdog(self, status:bool)->None:
        """Sets the Watchdog to the given status. (Activate if status is True)."""
        isAlive = self._dog.trigger_status(status, self.batchFile)
        if status and not isAlive:
            self._specify_batchfile()
            self._specify_watchdog_directory()


    ### Methods/Analysis

    def analyze_single_file(self, filename:str)->None:

        thread = Appender()
        thread.fileValidated.connect(self.add_file)
        # thread.importBatchTriggered.connect(self.update_batch)
        # self.cancelInitiated.connect(thread.cancel_job)
        thread.append(filename, self.batchFile, self.setting)


    def analyze(self)->None:
        self._logger.info("Start batch analysis.")

        # Get the modus.
        isUpdatePlot = self._window.get_update_plots()
        isExportBatch = self._window.get_export_batch() or self._window.get_plot_trace()

        files = self._files.to_list()

        if not files:
            return

        if isExportBatch and not self.batchFile:
            self._specify_batchfile()
            return

        if isUpdatePlot:
            self._thread = Plotter()
            self._thread.fileTriggered.connect(self.parent().plot_spectrum)
            self.cancelInitiated.connect(self._thread.cancel_job)
            self._thread.plot(files)

        if isExportBatch:
            self._thread = Exporter()
            self.cancelInitiated.connect(self._thread.cancel_job)
            self._thread.finished.connect(self.update_batch)
            self._thread.progressChanged.connect(self._window.set_progress_bar)
            self._thread.skippedFilesTriggered.connect(self.handle_skipped_files)
            self._thread.export(files, self.batchFile, self.setting)


    def import_batchfile(self, takeCurrentBatchfile:bool=False)->None:
        # Select the file from which the data shall be imported.
        filename = self._determine_batchfile(takeCurrentBatchfile)
        if not filename:
            return

        # Define the specific value which shall be plotted.
        columnValue = self._window.traceSelection
        try:
            file = FileReader(filename, columnValue=columnValue)
        except FileNotFoundError:
            return

        if not file.is_valid_batchfile():
            return

        # TODO: See #98
        self._traceSpectrum.reset_time()
        for peak in file.data.keys():
            timestamps, values = zip(*file.data[peak])
            diffTimes = self._traceSpectrum.calculate_time_differences(timestamps)
            traceData = np.array((diffTimes, values)).transpose()
            file.data[peak] = traceData

        # Plot the trace.
        self._traceSpectrum.set_custom_yLabel(columnValue)
        self._traceSpectrum.set_data(file.data)


    def _determine_batchfile(self, takeCurrentBatchfile:bool)->str:
        """Takes either the current batchfile or opens a dialog to select one."""
        if takeCurrentBatchfile:
            filename = self.batchFile
        else:
            filename = dialog.dialog_importBatchfile()
        return filename


    def set_setting(self, setting:BasicSetting)->None:
        validFittings =  []
        for fit in setting.checkedFittings:
            if fit.is_valid():
                validFittings.append(fit)
        setting.checkedFittings = validFittings
        self.setting = setting



    ### UI-interactions


    def _specify_batchfile(self)->None:
        """Specifies the filename through a dialog."""
        filename = dialog.dialog_batchfile()
        self.batchFile = filename


    def _specify_watchdog_directory(self, directory:str="")->None:
        """Specifies the watchdog directory through a dialog."""
        directory = directory if directory is None else dialog.dialog_watchdogDirectory()
        if directory is None or path.isdir(directory):
            self.WDdirectoryChanged.emit(directory)


    def _browse_spectra(self)->None:
        """Opens a dialog to browse for spectra and updates the filelist."""
        filelist = dialog.dialog_spectra()
        self.update_filelist(filelist)


    def open_indexed_file(self, index:(QModelIndex, int))->None:
        """
        Retrieve the data of the file of the list.

        Parameters
        ----------
        index : QModelIndex, int
            Transmitted by a QListModel or by another method.
        """
        index, msg = get_numerical_index(index)
        self._logger.info(msg)

        filename = self._get_indexed_filename(index)

        if filename:
            selectedFile = FileReader(filename)
            dogAlive = self._dog.is_alive()
            self.fileSelected.emit(selectedFile, dogAlive)
            self._traceSpectrum.plot_referencetime_of_spectrum(*selectedFile.fileinformation)


    def _get_indexed_filename(self, index:int)->str:
        try:
            filename = self._files[index]
        except IndexError:
            filename = None
            self._logger.info("Cannot open file, invalid index provided!")
        return filename


    ### Interaction with the FileSet self._files.


    def update_filelist(self, filelist:list)->None:
        """Updates the filelist."""
        self._files.update(filelist)
        self._logger.info("Filelist updated.")


    def reset_files(self)->None:
        """Resets the filelist."""
        self._files.clear()


    def reset_trace(self)->None:
        self._traceSpectrum = Trace(self._window.plotTraceSpectrum)
        self._traceSpectrum.reset_data()


    def reset_batchfile(self)->None:
        self.batchFile = None


    def reset_batch(self)->None:
        self.reset_files()
        self.reset_trace()
        self.reset_batchfile()
        self._trigger_watchdog(False)
        self._specify_watchdog_directory(None)


    def schedule_cancel_routine(self)->None:
        """Demands a cancellation. Processed in corresponing methods."""
        self.cancelInitiated.emit(True)



def get_numerical_index(index:(QModelIndex, int))->tuple:
    try:
        index = index.row()
        msg = "Open indexed file called by an event."
    except AttributeError:
        msg = "Open indexed file called by another method."
    return index, msg
