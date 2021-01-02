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
import numpy as np
from os import path

# third-party libs
from PyQt5.QtCore import Signal, QModelIndex
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import QKeySequence as QKeys

# local modules/libs
from ConfigLoader import ConfigLoader
from Logger import Logger
# UI
from ui.UIBatch import UIBatch
# modules & universal
import modules.Universal as uni
import dialog_messages as dialog
from modules.dataanalysis.SpectrumHandler import SpectrumHandler
from modules.dataanalysis.Trace import Trace
from modules.Watchdog import Watchdog
from modules.filehandling.filereading.FileReader import FileReader
from modules.filehandling.filewriting.BatchWriter import BatchWriter


# Enums
from c_types.FileSet import FileSet
from c_types.BasicSetting import BasicSetting
from c_enum.CHARACTERISTIC import CHARACTERISTIC as CHC
from c_enum.ERROR_CODE import ERROR_CODE as ERR
from c_enum.SUFFICES import SUFFICES as SUFF

# exceptions
from exception.InvalidSpectrumError import InvalidSpectrumError

# constants
# BATCH_SUFFIX requires "." as prefix to the suffix-value
BATCH_SUFFIX = "." + SUFF.BATCH.value



class BatchAnalysis(QDialog):
    """
    Provides an dialog widget as interface to analyze multiple spectra.

    Provides a multiple file handling interface.
    May extract characteristic values for further applications.

    Usage:
        from modules.BatchAnalysis import BatchAnalysis
        batch = BatchAnalysis(parent)  # parent as main window or application

    """

    BATCH = ConfigLoader().BATCH

    # Qt-Signals
    signal_enableAnalysis = Signal(bool)
    signal_batchfile = Signal(str)
    signal_WDdirectory = Signal(str)
    signal_enableWD = Signal(bool)
    signal_progress = Signal(float)


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
        self.logger = Logger(__name__)

        # Initialize the parent class [equivalent to: QDialog.__init__(self)].
        super().__init__(parent)

        # Init the props to prevent errors in the ui-init routine.
        # (SystemError: <built-in function connectSlotsByName> returned a result with an error set)
        self._batchFile = None
        self._WDdirectory = ""
        self.currentFile = None
        self.isScheduledCancel = False
        self.setting = None

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
        self.window.connect_browse_spectra(self.browse_spectra)
        self.window.connect_analyze(self.analyze)
        self.window.connect_cancel(self.schedule_cancel_routine)
        self.window.connect_change_batchfile(self.enable_analysis)
        self.window.connect_change_trace(self.import_batchfile)
        self.window.connect_clear(self.reset_batch)
        self.window.connect_import_batchfile(self.import_batchfile)
        self.window.connect_select_file(self.open_indexed_file)
        self.window.connect_select_file(self.enable_analysis)
        self.window.connect_set_watchdog_directory(self.specify_watchdog_directory)
        self.window.connect_set_batchfile(self.specify_batchfile)
        self.window.connect_watchdog(self.toggle_watchdog)

        self.signal_batchfile.connect(self.window.slot_batchfile)
        self.signal_enableAnalysis.connect(self.window.slot_enableAnalysis)
        self.signal_WDdirectory.connect(self.window.slot_WDdirectory)
        self.signal_enableWD.connect(self.window.slot_enableWD)
        self.signal_progress.connect(self.window.slot_progress)


    ### Events
    ### UI-interactions

    def closeEvent(self, event)->None:
        """Closing the BatchAnalysis dialog to have a clear shutdown."""
        event.accept()
        self.schedule_cancel_routine()
        self.deactivate_watchdog()


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
            self.logger.debug("No invalid url found.")

        self.update_filelist(valid_urls)


    ### Watchdog routines

    def watchdog_event_handler(self, pathname:str)->None:
        # Checks absolute pathnames to avoid issues due to relative vs absolute pathnames.
        eventPath, _, _ = uni.extract_path_basename_suffix(pathname)

        self.logger.info("WD: Spectrum file modified/added: %s"%(pathname))
        isOk = self.analyze_single_file(pathname)
        if not isOk:
            return
        self.update_filelist([pathname])
        return

        # Distinguish between modified batch- and spectrum-file.
        if self.batchFile == pathname:
            self.logger.info("WD: Batchfile modified.")
            self.import_batchfile(takeCurrentBatchfile=True)
        elif self.WDdirectory == eventPath:
            self.logger.info("WD: Spectrum file modified/added: %s"%(pathname))
            isOk = self.analyze_single_file(pathname)
            if not isOk:
                return
            self.update_filelist([pathname])
            # self._files.select_row_by_filename(pathname)


    def toggle_watchdog(self, status:bool)->None:
        """Sets the Watchdog to the given status. (Activate if status is True)."""
        if status:
            self.activate_watchdog()
        else:
            self.deactivate_watchdog()


    def has_valid_WD_settings(self)->bool:
        isWDdir = path.isdir(self.WDdirectory) or self.logger.info("Invalid WD directory!")
        batchPath, _, _ = uni.extract_path_basename_suffix(self.batchFile)
        isBatchdir = path.isdir(batchPath) or self.logger.info("Invalid batch directory!")
        isValid = (isWDdir and isBatchdir)
        return isValid


    def activate_watchdog(self)->None:
        """Activates the WD if corresponding paths are valid."""
        if not self.has_valid_WD_settings():
            self.signal_enableWD.emit(True)
            return

        WDpath = self.WDdirectory
        batchPath, _, _ = uni.extract_path_basename_suffix(self.batchFile)
        paths = [WDpath]
        self.dog.start(paths)
        self.signal_enableWD.emit(False)


    def deactivate_watchdog(self)->None:
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

        data, header = self.analyze_file(self.setting, specHandler)
        self.export_batch(data, header, isUpdate=True)
        self.import_batchfile(takeCurrentBatchfile=True)
        return ERR.OK


    def analyze(self)->None:
        self.logger.info("Start batch analysis.")

        # Reset the properties to have a clean setup.
        self.isScheduledCancel = False

        # Get the modus.
        isUpdatePlot = self.window.get_update_plots()
        isPlotTrace = self.window.get_plot_trace()
        # Export even if plot trace is selected(First export then import+plot).
        isExportBatch = self.window.get_export_batch() or isPlotTrace

        # Get characteristic values.
        basicSetting = self.setting

        data = []
        skippedFiles = []

        files = self._files.to_list()
        amount = len(files)
        self.logger.info("No. of files %i:"%(amount))

        for i in range(amount):
            # Be responsive and process events to enable cancelation.
            # HINT: QApplication.processEvents() slows down the analysis massively.
            QApplication.processEvents()
            if self.isScheduledCancel:
                break

            self.signal_progress.emit((i+1)/amount)

            # Read out the filename and the data.
            file = files[i]
            try:
                self.currentFile = FileReader(file)
            except FileNotFoundError:
                skippedFiles.append(file)
                continue

            if isExportBatch:
                if not self.currentFile.is_analyzable():
                    skippedFiles.append(file)
                    continue

                try:
                    specHandler = SpectrumHandler(self.currentFile, basicSetting)
                except InvalidSpectrumError:
                    skippedFiles.append(file)
                    continue

                fileData, header = self.analyze_file(basicSetting, specHandler)
                data.extend(fileData)

            # Select by filename to trigger event based update of the plot.
            elif isUpdatePlot:
                self._files.select_row_by_filename(file)

        if isExportBatch:
            self.export_batch(data, header)

        if isPlotTrace:
            self.import_batchfile(takeCurrentBatchfile=True)

        # Prompt the user with information about the skipped files.
        dialog.information_batchAnalysisFinished(skippedFiles)
        self._files.difference_update(skippedFiles)


    def merge_characteristics(self, specHandler:SpectrumHandler)->dict:
        results = specHandler.results
        results[CHC.FILENAME] = self.currentFile.filename

        timestamp = self.currentFile.timeInfo
        results[CHC.HEADER_INFO] = uni.timestamp_to_string(timestamp)
        return results


    def analyze_file(self, setting:BasicSetting, specHandler:SpectrumHandler)->tuple:
        data = []
        for fitting in setting.checkedFittings:
            specHandler.fit_data(fitting)
            results = self.merge_characteristics(specHandler)

            # excluding file if no appropiate data given like in processed spectra.
            if not specHandler.has_valid_peak():
                continue

            data.append(assemble_row(results))
        header = assemble_header(results)
        return data, header


    def import_batchfile(self, takeCurrentBatchfile:bool=False)->None:

        # Select the file from which the data shall be imported.
        filename = self.determine_batchfile(takeCurrentBatchfile)
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


    def determine_batchfile(self, takeCurrentBatchfile:bool)->str:
        """Takes either the current batchfile or opens a dialog to select one."""
        if takeCurrentBatchfile:
            filename = self.batchFile
        else:
            filename = dialog.dialog_importBatchfile()
        return filename


    def export_batch(self, data:list, header:list, isUpdate:bool=False)->None:
        exportWriter = BatchWriter(self.batchFile)
        if isUpdate:
            exportWriter.extend_data(data, header)
        else:
            exportWriter.export(data, header)


    def set_setting(self, setting:BasicSetting)->None:
        validFittings =  []
        for fit in setting.checkedFittings:
            if fit.is_valid():
                validFittings.append(fit)
        setting.checkedFittings = validFittings
        self.setting = setting



    ### UI-interactions


    def specify_batchfile(self)->None:
        """Specifies the filename through a dialog."""
        filename = dialog.dialog_batchfile()
        self.batchFile = filename


    def specify_watchdog_directory(self)->None:
        """Specifies the watchdog directory through a dialog."""
        directory = dialog.dialog_watchdogDirectory()
        self.WDdirectory = directory


    def browse_spectra(self)->None:
        """Opens a dialog to browse for spectra and updates the filelist."""
        filelist = dialog.dialog_spectra()
        self.update_filelist(filelist)


    def enable_analysis(self)->None:
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
        self.logger.debug(msg)

        filename = self.get_indexed_filename(index)

        if filename:
            selectedFile = FileReader(filename)
            dogAlive = self.dog.is_alive()
            self.parent().apply_file(selectedFile, silent=dogAlive)
            self.traceSpectrum.plot_referencetime_of_spectrum(*selectedFile.fileinformation)


    def get_indexed_filename(self, index:int)->str:
        try:
            filename = self._files[index]
        except IndexError:
            filename = None
            self.logger.info("Cannot open file, invalid index provided!")
        return filename


    ### Interaction with the FileSet self._files.


    def update_filelist(self, filelist:list)->None:
        """Updates the filelist and refreshes the ui."""
        for filename in filelist:
            if not uni.is_valid_suffix(filename):
                filelist.remove(filename)
        self._files.update(filelist)
        self.logger.debug("Filelist updated.")


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
        self.isScheduledCancel = True


def assemble_header(config:dict)->list:
    header = [label.value for label in config.keys()]
    return header


def assemble_row(config:dict)->list:
    row = config.values()
    return row


def get_numerical_index(index:(QModelIndex, int))->tuple:
    try:
        index = index.row()
        msg = "Open indexed file called by an event."
    except AttributeError:
        msg = "Open indexed file called by another method."
    return index, msg
