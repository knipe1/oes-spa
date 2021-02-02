#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glossary:
    batchfile: The file in which the characteristic values are exported to.
    WDdirectory: Directory which is observed by the WatchDog (WD)

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
from PyQt5.QtCore import Signal, Slot, QModelIndex
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QKeySequence as QKeys

# local modules/libs
# UI
from ui.UIBatch import UIBatch
# modules & universal
import modules.Universal as uni
import dialog_messages as dialog
import modules.dataanalysis.Analysis as Analysis
from modules.dataanalysis.SpectrumHandler import SpectrumHandler
from modules.dataanalysis.Trace import Trace
from modules.Watchdog import Watchdog
from modules.filehandling.filereading.FileReader import FileReader
from modules.filehandling.filewriting.BatchWriter import BatchWriter
from modules.thread.Exporter import Exporter
from modules.thread.Plotter import Plotter


# Enums
from c_types.FileSet import FileSet
from c_types.BasicSetting import BasicSetting
from c_enum.ERROR_CODE import ERROR_CODE as ERR
from c_enum.SUFFICES import SUFFICES as SUFF

# exceptions
from exception.InvalidSpectrumError import InvalidSpectrumError

# constants
BATCH_SUFFIX = SUFF.BATCH


class BatchAnalysis(QDialog):
    """
    Provides an dialog widget as interface to analyze multiple spectra.

    Provides a multiple file handling interface.
    May extract characteristic values for further applications.

    Usage:
        from modules.BatchAnalysis import BatchAnalysis
        batch = BatchAnalysis(parent)  # parent as main window or application

    """

    # Qt-Signals
    signal_enableAnalysis = Signal(bool)
    signal_batchfile = Signal(str)
    signal_WDdirectory = Signal(str)
    signal_enableWD = Signal(bool)
    signal_file = Signal(str)
    signal_cancel = Signal(bool)

    ### Slots

    @Slot()
    def slot_import_batch(self):
        if self.window.get_plot_trace():
            self.import_batchfile(takeCurrentBatchfile=True)


    @Slot(list)
    def slot_handle_skipped_files(self, skippedFiles:list):
        dialog.information_batchAnalysisFinished(skippedFiles)
        self._files.difference_update(skippedFiles)


    ### Properties

    @property
    def batchFile(self)->str:
        return self._batchFile

    @batchFile.setter
    def batchFile(self, filename:str)->None:
        """batchFile setter: Updating the ui"""
        if not filename:
            return
        filename = uni.replace_suffix(filename, suffix=BATCH_SUFFIX)
        self._batchFile = filename
        self.signal_batchfile.emit(filename)


    @property
    def WDdirectory(self)->str:
        return self._WDdirectory

    @WDdirectory.setter
    def WDdirectory(self, directory:str)->None:
        """WDdirectory setter: Updating the ui"""
        if not path.isdir(directory):
            return
        self._WDdirectory = directory
        self.signal_WDdirectory.emit(directory)


    def __init__(self, parent)->None:
        """
        Parameters
        ----------
        parent : AnalysisWindow
            Required for the interplay between the two windows.

        """
        self._logger = logging.getLogger(__name__)

        # Initialize the parent class [equivalent to: QDialog.__init__(self)].
        super().__init__(parent)

        # Init the props to prevent errors in the ui-init routine.
        # (SystemError: <built-in function connectSlotsByName> returned a result with an error set)
        self._batchFile = None
        self._WDdirectory = ""
        self.currentFile = None
        self.setting = None
        self._thread = None

        # Set up ui.
        self.window = UIBatch(self)
        self.__post_init__()


    def __post_init__(self)->None:
        self._files = FileSet(listWidget=self.window.listFiles)
        self.dog = Watchdog(self.watchdog_event_handler)
        self.traceSpectrum = Trace(self.window.plotTraceSpectrum)

        # Link events of the ui to methods of this class.
        self.set_connections()



    def __repr__(self)->str:
        info = {}
        info["batchfile"] = self.batchFile
        info["files"] = self._files
        return self.__module__ + ":\n" + str(info)


    def set_connections(self)->None:
        self.window.connect_browse_spectra(self._browse_spectra)
        self.window.connect_analyze(self.analyze)
        self.window.connect_cancel(self.schedule_cancel_routine)
        self.window.connect_change_batchfile(self._enable_analysis)
        self.window.connect_change_trace(self.import_batchfile)
        self.window.connect_clear(self.reset_batch)
        self.window.connect_import_batchfile(self.import_batchfile)
        self.window.connect_select_file(self.open_indexed_file)
        self.window.connect_select_file(self._enable_analysis)
        self.window.connect_set_watchdog_directory(self._specify_watchdog_directory)
        self.window.connect_set_batchfile(self._specify_batchfile)
        self.window.connect_watchdog(self._toggle_watchdog)

        self.signal_batchfile.connect(self.window.slot_batchfile)
        self.signal_enableAnalysis.connect(self.window.slot_enableAnalysis)
        self.signal_WDdirectory.connect(self.window.slot_WDdirectory)
        self.signal_enableWD.connect(self.window.slot_enableWD)


    ### Events
    ### UI-interactions

    def closeEvent(self, event)->None:
        """Closing the BatchAnalysis dialog to have a clear shutdown."""
        event.accept()
        self.schedule_cancel_routine()
        self._deactivate_watchdog()


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
        isFocused = self.window.is_focussed_filelist()
        isDelete = event.matches(QKeys.Delete)
        if isFocused and isDelete:
            row = self._files.selected_row
            self._files.remove(self._files[row])
            return


    def dragEnterEvent(self, event)->None:
        """Note: Validation takes place in dropEvent-handler."""
        event.accept()


    def dropEvent(self, event)->None:
        """Filter the dropped urls to update the files with only valid urls."""
        urls = event.mimeData().urls()
        valid_urls = set()
        for url in urls:
            localUrl = uni.get_valid_local_url(url)
            valid_urls.add(localUrl)

        try:
            valid_urls.remove(None)
            dialog.critical_unknownSuffix(parent=self)
        except KeyError:
            self._logger.info("No invalid url found.")

        self.update_filelist(valid_urls)


    ### Watchdog routines

    def watchdog_event_handler(self, pathname:str)->None:
        self._logger.info("WD: Spectrum file modified/added: %s", pathname)
        isOk = self.analyze_single_file(pathname)
        if not isOk:
            return
        self.update_filelist([pathname])
        # self._files.select_row_by_filename(pathname)


    def _toggle_watchdog(self, status:bool)->None:
        """Sets the Watchdog to the given status. (Activate if status is True)."""
        if status:
            self._activate_watchdog()
        else:
            self._deactivate_watchdog()


    def _has_valid_WD_settings(self)->bool:
        isWDdir = path.isdir(self.WDdirectory) or self._logger.info("Invalid WD directory!")
        batchPath, _, _ = uni.extract_path_basename_suffix(self.batchFile)
        isBatchdir = path.isdir(batchPath) or self._logger.info("Invalid batch directory!")
        isValid = (isWDdir and isBatchdir)
        return isValid


    def _activate_watchdog(self)->None:
        """Activates the WD if corresponding paths are valid."""
        if not self._has_valid_WD_settings():
            self.signal_enableWD.emit(True)
            return

        WDpath = self.WDdirectory
        self.dog.start(WDpath)
        self.signal_enableWD.emit(False)


    def _deactivate_watchdog(self)->None:
        self.dog.stop()
        self.signal_enableWD.emit(True)


    ### Methods/Analysis

    def analyze_single_file(self, filename:str)->None:

        self.currentFile = FileReader(filename)
        if not self.currentFile.is_analyzable():
            return None

        try:
            specHandler = SpectrumHandler(self.currentFile, self.setting)
        except InvalidSpectrumError:
            return None

        data, header = Analysis.analyze_file(self.setting, specHandler, self.currentFile)
        BatchWriter(self.batchFile).extend_data(data, header)
        self.import_batchfile(takeCurrentBatchfile=True)
        return ERR.OK


    def analyze(self)->None:
        self._logger.info("Start batch analysis.")

        # Get the modus.
        isUpdatePlot = self.window.get_update_plots()
        isExportBatch = self.window.get_export_batch() or self.window.get_plot_trace()

        files = self._files.to_list()

        if isUpdatePlot:
            self._thread = Plotter()
            self._thread.signal_filename.connect(self.parent().slot_plot_spectrum)
            self.signal_cancel.connect(self._thread.slot_cancel)
            self._thread.plot(files)


        if isExportBatch:
            self._thread = Exporter()
            self.signal_cancel.connect(self._thread.slot_cancel)
            self._thread.finished.connect(self.slot_import_batch)
            self._thread.signal_progress.connect(self.window.slot_progress)
            self._thread.signal_skipped_files.connect(self.slot_handle_skipped_files)
            self._thread.export(files, self.batchFile, self.setting)


    def import_batchfile(self, takeCurrentBatchfile:bool=False)->None:

        # Select the file from which the data shall be imported.
        filename = self._determine_batchfile(takeCurrentBatchfile)
        if not filename:
            return

        # Define the specific value which shall be plotted.
        columnValue = self.window.currentTraceValue
        try:
            file = FileReader(filename, columnValue=columnValue)
        except FileNotFoundError:
            return

        if not file.is_valid_batchfile():
            return

        # See #98
        self.traceSpectrum.reset_time()
        for peak in file.data.keys():
            timestamps, values = zip(*file.data[peak])
            diffTimes = self.traceSpectrum.calculate_time_differences(timestamps)
            traceData = np.array((diffTimes, values)).transpose()
            file.data[peak] = traceData

        # Plot the trace.
        self.traceSpectrum.set_custom_yLabel(columnValue)
        self.traceSpectrum.update_data(file.data)


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


    def _specify_watchdog_directory(self)->None:
        """Specifies the watchdog directory through a dialog."""
        directory = dialog.dialog_watchdogDirectory()
        self.WDdirectory = directory


    def _browse_spectra(self)->None:
        """Opens a dialog to browse for spectra and updates the filelist."""
        filelist = dialog.dialog_spectra()
        self.update_filelist(filelist)


    def _enable_analysis(self)->None:
        """Enables the ui if configuration is set accordingly."""
        if not self.batchFile:
            enable = False
        elif not self._files:
            enable = False
        else:
            enable = True

        self.signal_enableAnalysis.emit(enable)


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
            dogAlive = self.dog.is_alive()
            self.parent().apply_file(selectedFile, silent=dogAlive)
            self.traceSpectrum.plot_referencetime_of_spectrum(*selectedFile.fileinformation)


    def _get_indexed_filename(self, index:int)->str:
        try:
            filename = self._files[index]
        except IndexError:
            filename = None
            self._logger.info("Cannot open file, invalid index provided!")
        return filename


    ### Interaction with the FileSet self._files.


    def update_filelist(self, filelist:list)->None:
        """Updates the filelist and refreshes the ui."""
        for filename in filelist:
            if not uni.is_valid_suffix(filename):
                filelist.remove(filename)
        self._files.update(filelist)
        self._logger.info("Filelist updated.")


    def reset_files(self)->None:
        """Resets the filelist."""
        self._files.clear()


    def reset_trace(self)->None:
        self.traceSpectrum = Trace(self.window.plotTraceSpectrum)
        self.traceSpectrum.update_data({})


    def reset_batch(self)->None:
        self.reset_files()
        self.reset_trace()


    def schedule_cancel_routine(self)->None:
        """Demands a cancellation. Processed in corresponing methods."""
        self.signal_cancel.emit(True)



def get_numerical_index(index:(QModelIndex, int))->tuple:
    try:
        index = index.row()
        msg = "Open indexed file called by an event."
    except AttributeError:
        msg = "Open indexed file called by another method."
    return index, msg
