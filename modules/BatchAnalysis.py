#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glossary:
    batchfile: The file in which the characteristic values are exported to.
    WDdirectory: Directory which is observed by the WatchDog (WD)


Created on Mon Jan 20 10:22:44 2020

@author: Hauke Wernecke
"""

# standard libs
import numpy as np
from os import path

# third-party libs
from PyQt5.QtCore import QFileInfo, QModelIndex
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
from modules.dataanalysis.Spectrum import Spectrum
from modules.Watchdog import Watchdog
from modules.filehandling.filereading.FileReader import FileReader
from modules.filehandling.filewriting.BatchWriter import BatchWriter
from modules.dataanalysis.SpectrumHandler import SpectrumHandler


# Enums
from custom_types.FileSet import FileSet
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC
from custom_types.EXPORT_TYPE import EXPORT_TYPE
from custom_types.ERROR_CODE import ERROR_CODE as ERR


# constants


class BatchAnalysis(QDialog):
    """
    Provides an dialog widget as interface to analyze multiple spectra.

    Provides a multiple file handling interface.
    May extract characteristic values for further applications.

    Usage:
        from modules.BatchAnalysis import BatchAnalysis
        batch = BatchAnalysis(parent)  # parent as main window or application

    """

    # Load the configuration for batch analysis and export.
    config = ConfigLoader()
    BATCH = config.BATCH;


    ### Properties

    @property
    def batchFile(self):
        """batchFile getter"""
        return self._batchFile

    @batchFile.setter
    def batchFile(self, filename:str):
        """batchFile setter: Updating the ui"""
        self._batchFile = filename
        try:
            self.window.batchFile = filename
        except AttributeError:
            pass


    @property
    def WDdirectory(self):
        """WDdirectory getter"""
        return self._WDdirectory

    @WDdirectory.setter
    def WDdirectory(self, path:str):
        """WDdirectory setter: Updating the ui"""
        self._WDdirectory = path
        try:
            self.window.WDdirectory = path
        except AttributeError:
            pass


    @property
    def lastdir(self):
        """lastdir getter"""
        return self.parent().lastdir

    @lastdir.setter
    def lastdir(self, path:str):
        """lastdir setter: Updating the parent"""
        self.parent().lastdir = path



    def __init__(self, parent):
        """
        Parameters
        ----------
        parent : AnalysisWindow
            Important for the interplay between the two windows.

        Returns
        -------
        None.

        """

        # Set up the logger.
        self.logger = Logger(__name__)
        self.logger.info("Init BatchAnalysis")

        # Initialize the parent class ( == QDialog.__init__(self).
        super().__init__(parent)

        # Init the props to prevent errors in the ui-init routine.
        self.batchFile = None
        self.WDdirectory = None

        # Set up ui.
        self.window = UIBatch(self)

        self.__post_init__()


    def __post_init__(self):
        # Set the defaults.
        self._files = FileSet(listWidget = self.window.listFiles)
        self.batchFile = self.window.batchFile
        self.WDdirectory = self.window.WDdirectory
        self.dog = Watchdog(self.watchdog_event_handler)
        self.traceSpectrum = Spectrum(self.window.mplTrace, EXPORT_TYPE.BATCH)

        # Link events of the ui to methods of this class.
        self.set_connections()


    def __repr__(self):
        info = {}
        info["batchfile"] = self.batchFile
        info["files"] = self._files
        info["lastdir"] = self.lastdir
        return self.__module__ + ":\n" + str(info)


    def set_connections(self):
        self.window.connect_browse_files(self.browse_spectra)
        self.window.connect_calculate(self.analyze)
        self.window.connect_cancel(self.schedule_cancel_routine)
        self.window.connect_change_csvfile(self.enable_analysis)
        self.window.connect_clear(self.reset_files)
        self.window.connect_import_batch(self.import_batchfile)
        self.window.connect_select_file(self.open_indexed_file)
        self.window.connect_select_file(self.enable_analysis)
        self.window.connect_set_filename(self.specify_batchfile)
        self.window.connect_change_trace(self.import_batchfile)
        self.window.connect_set_directory(self.specify_watchdog_directory)
        self.window.connect_watchdog(self.toggle_watchdog)

    ### Events
    ### UI-interactions

    def closeEvent(self, event):
        """Closing the BatchAnalysis dialog to have a clear shutdown."""
        self.deactivate_watchdog()


    def keyPressEvent(self, event):
        """
        Key handling.

        Regarding deletions, cancellations,...
        """

        isFocused = self.window.focussed_filelist()
        isDelete = event.matches(QKeys.Delete)
        isCancel = event.matches(QKeys.Cancel)

        # Remove currently selected file.
        if isFocused and isDelete:
            row = self._files.selected_row
            self._files.remove(self._files[row])

        # Cancel current analysis
        if isCancel:
            self.schedule_cancel_routine()


    def dragEnterEvent(self, event):
        """
        Drag file over window event.

        Always accepted, validation takes place in dropEvent-handler.
        """

        # Accept event, validation takes place in dropEvent-handler.
        event.accept();


    def dropEvent(self, event)->None:
        """
        Filter the dropped urls to update the files with only valid urls.

        Parameters
        ----------
        event : event
            The event itself.

        """

        # Set up a list to append valid files.
        valid_urls = set()

        # Get the urls and check their validity.
        urls = event.mimeData().urls();
        for url in urls:
            localUrl = uni.get_valid_local_url(url)
            valid_urls.add(localUrl)

        try:
            valid_urls.remove(None)
            dialog.critical_unknownSuffix(parent=self)
        except KeyError:
            self.logger.debug("No invalid url found.")

        # Updates the filelist with the valid urls.
        self.update_filelist(valid_urls)


    ### Watchdog routines

    def watchdog_event_handler(self, path:str)->None:
        # Checks absolute paths to avoid issues due to relative vs absolute paths.
        eventPath, _, _ = uni.extract_path_basename_suffix(path)

        # Distinguish between modified batch- and spectrum-file.
        if self.batchFile == path:
            self.logger.info("WD: Batchfile modified.")
            self.import_batchfile(takeCurrentBatchfile=True)
        elif self.WDdirectory == eventPath:
            self.logger.info("WD: Spectrum file modified/added: %s"%(path))
            errorcode = self.analyze(path)
            if not errorcode ==ERR.OK:
                return
            self.update_filelist([path])
            self._files.select_row_by_filename(path)


    def toggle_watchdog(self, status:bool)->None:
        """
        Sets the Watchdog to the given status. (Activate if status is True).
        """

        if status:
            self.activate_watchdog()
        else:
            self.deactivate_watchdog()


    def activate_watchdog(self)->None:
        """
        Activates the WD if corresponding paths are valid.

        """

        isValid = True
        # Prequerities given if WDpath and batchpath are defined.
        WDpath = self.WDdirectory
        if not path.isdir(WDpath):
            self.logger.warning("WDpath not defined: %s"%(WDpath))
            isValid = False

        batchPath = QFileInfo(self.batchFile).path()
        if not path.isdir(batchPath):
            self.logger.warning("batchPath not defined: %s"%(batchPath))
            isValid = False

        if not isValid:
            self.window.btnWatchdog.setChecked(False)
            return

        try:
            # Start WD for batchfile
            self.dog.start(WDpath)

            # Start WD for spectra directory (if they differ).
            if not (WDpath == batchPath):
                self.dog.start(batchPath)

            self.window.enable_WD(False)
        except AttributeError:
            self.logger.error("Error: No dog initialized!")


    def deactivate_watchdog(self)->None:
        self.dog.stop()
        self.window.enable_WD(True)


    ### Methods/Analysis

    def analyze(self, singleFile=None):
        self.logger.info("Analyze file.")

        # Reset the properties to have a clean setup.
        self.isScheduledCancel = False

        isSingleFile = bool(singleFile)
        if isSingleFile:
            singleFile = [singleFile]

        # Get the modus.
        isUpdatePlot = self.window.get_update_plots() and not isSingleFile
        isPlotTrace = self.window.get_plot_trace()
        # Export even if plot trace is selected(First export then import+plot).
        isExportBatch = self.window.get_export_batch() or isPlotTrace

        # Get characteristic values.
        basicSetting = self.parent().window.get_basic_setting()

        data = []
        skippedFiles = []

        # Either singleFile is given by a filename, then the amount of files=1,
        # Otherwise the filelist is used.
        files = singleFile or self._files.to_list()
        amount = len(files)
        self.logger.info("No. of files %i:"%(amount))

        for i in range(amount):
            config = retrieve_batch_config()

            # Be responsive and process events to enable cancelation.
            QApplication.processEvents()
            if self.isScheduledCancel:
                break

            # Update process bar
            self.window.update_progressbar((i+1)/amount)

            # Read out the filename and the data.
            file = files[i]
            self.currentFile = FileReader(file)

            errorcode = self.currentFile.is_valid_spectrum()
            if not errorcode:
                if isSingleFile:
                    return errorcode
                else:
                    skippedFiles.append(file)
                    continue

            if isExportBatch:
                # Get the data.
                specHandler = SpectrumHandler(basicSetting)
                errorcode = specHandler.analyse_data(self.currentFile)
                if not errorcode:
                    return errorcode

                avg = specHandler.avgbase
                peakHeight = specHandler.peakHeight
                peakArea = specHandler.peakArea
                peakPosition = specHandler.peakPosition
                characteristicValue = specHandler.characteristicValue
                timestamp = self.currentFile.timeInfo

                # excluding file if no appropiate data given like in processed
                # spectra.
                # TODO: validate_results as method of specHandler? Would also omit
                # the assignemts above!?
                if not peakHeight:
                    skippedFiles.append(file)
                    continue

                config[CHC.FILENAME] = file
                config[CHC.BASELINE] = avg
                config[CHC.CHARACTERISTIC_VALUE] = characteristicValue
                config[CHC.PEAK_AREA] = peakArea
                config[CHC.PEAK_HEIGHT] = peakHeight
                config[CHC.PEAK_POSITION] = peakPosition
                # Convert to string for proper presentation.
                config[CHC.HEADER_INFO] = uni.timestamp_to_string(timestamp)

                data.append(assemble_row(config))

            # Select by filename to trigger event based update of the plot.
            if isUpdatePlot:
                self._files.select_row_by_filename(file)

        if isExportBatch:
            # Get the name of the peak for proper description.
            peakName = basicSetting.fitting.peak.name
            header = assemble_header(config, peakName=peakName)
            if isSingleFile:
                data = assemble_row(config)

            self.export_batch(data, header, isUpdate=isSingleFile)

        if isPlotTrace:
            self.import_batchfile(takeCurrentBatchfile=True)


        # Prompt the user with information about the skipped files.
        if not isSingleFile:
            dialog.information_batchAnalysisFinished(skippedFiles)
            self._files.difference_update(skippedFiles)

        return ERR.OK



    def import_batchfile(self, takeCurrentBatchfile=False):
        # Define the specific value which shall be plotted.
        columnValue = self.window.currentTraceValue

        # Select the file from which the data shall be imported.
        filename = self.determine_batchfile(takeCurrentBatchfile)
        if not filename:
            return

        file = FileReader(filename, columnValue=columnValue)
        if not file.is_valid_batchfile():
            return

        # TODO: Check sorting of 2D arrays make sense here.
        timestamps, values = file.data
        diffTimes = self.calculate_time_differences(timestamps)
        traceData = (diffTimes, values)

        # Plot the trace.
        self.traceSpectrum.set_custom_y_label(columnValue)
        self.traceSpectrum.update_data(traceData)
        self.traceSpectrum.plot_spectrum()

        return


    def determine_batchfile(self, takeCurrentBatchfile):
        if takeCurrentBatchfile:
            filename = self.batchFile
        else:
            filename = dialog.dialog_openBatchFile()
            # filename = dialog.dialog_openBatchFile(self.lastdir)
            self.lastdir = filename
        return filename


    def calculate_time_differences(self, timestamps):
        diffTimes = np.zeros((len(timestamps),))

        for idx, timestamp in enumerate(timestamps):
            diffTime = self.traceSpectrum.get_timediff_H(timestamp)
            diffTimes[idx] = diffTime
        return diffTimes


    def export_batch(self, data, header, isUpdate=False):
        csvWriter = BatchWriter(self.batchFile)
        if isUpdate:
            csvWriter.extend_data(data, header)
        else:
            csvWriter.export(data, header)



    ### UI-interactions


    def specify_batchfile(self):
        """
        Specifies the filename through a dialog.

        Determines the batchfile, and updates the ui.

        Returns
        -------
        filename : str
            The filename selected by the user.
            None if dialog was quit or cancelled.

        """
        # Retrieve the filename and the corresponding info
        filename = dialog.dialog_batchfile()
        # filename = dialog.dialog_batchfile(self.lastdir)

        # Cancel or quit the dialog.
        if not filename:
            return

        filename = uni.replace_suffix(filename)

        # Change interface and preset for further dialogs (lastdir)
        self.lastdir = filename
        self.batchFile = filename

        return filename


    def specify_watchdog_directory(self):
        directory = dialog.dialog_watchdogDirectory()
        # directory = dialog.dialog_watchdogDirectory(self.lastdir)

        if directory:
            self.WDdirectory = directory
            self.lastdir = directory


    def browse_spectra(self):
        """Opens a dialog to browse for spectra and updates the filelist."""
        filelist = dialog.dialog_spectra()
        # filelist = dialog.dialog_spectra(self.lastdir)
        self.update_filelist(filelist)
        try:
            filename = filelist[0]
            self.lastdir = filename
        except IndexError:
            self.logger.info("Browse Spectra: Could not update directory.")


    def enable_analysis(self):
        """
        Enables the ui if configureation is set accordingly.
        """
        enable = True;

        # Check for specified batchFile
        if not self.batchFile:
            enable = False
        elif not self._files:
            enable = False

        self.window.enable_analysis(enable)


    def open_indexed_file(self, index:(QModelIndex, int)):
        """
        Retrieve the data of the selected file of the list.

        Used for applying the data after clicking on the list.
        """

        # Distinguish given index by numerical value (from another method) or
        # is given by the ListModel (by an event)
        try:
            index = index.row()
        except AttributeError:
            self.logger.debug("Open indexed file called programmatically.")

        try:
            selectedFilename = self._files[index]
            selectedFile = FileReader(selectedFilename)
            if selectedFile:
                if self.dog.is_alive():
                    self.parent().apply_file(selectedFile, silent=True)
                else:
                    self.parent().apply_file(selectedFilename)
                self.traceSpectrum.plot_referencetime_of_spectrum(*selectedFile.fileinformation)
        except IndexError:
            self.logger.info("Cannot open file, invalid index provided!")


    ### Interaction with the FileSet self._files.


    def update_filelist(self, filelist:list):
        """
        Updates the filelist and refreshes the ui.

        Provides the interface for other modules.

        Parameters
        ----------
        filelist : list of strings
            List of strings including valid urls/filenames.

        Returns
        -------
        None.

        """

        for filename in filelist:
            if not uni.is_valid_suffix(filename):
                filelist.remove(filename)
        self._files.update(filelist)
        self.logger.debug("Filelist updated.")


    def reset_files(self):
        """Resets the filelist."""
        self._files.clear()


    def schedule_cancel_routine(self):
        """Demands a cancellation. Processed in corresponing methods."""
        self.isScheduledCancel = True



def assemble_header(config:dict, peakName="")->list:
    characteristicLabel = CHC.CHARACTERISTIC_VALUE.value

    header = [label.value for label in config.keys()]

    # Replace 'Characteristic value' with proper name.
    if peakName:
        idx = header.index(characteristicLabel)
        header[idx] = characteristicLabel + " (%s)"%(peakName)

    return header


def assemble_row(config:dict)->list:
    row = [value for value in config.values()]
    return row


def retrieve_batch_config()->dict:
    """
    Returns
    -------
    config: dict
        Containts the CHARACTERISTIC enum as dict with default values.

    """

    config = {CHC.FILENAME: None,
              CHC.PEAK_HEIGHT: None,
              CHC.PEAK_AREA: None,
              CHC.BASELINE: None,
              CHC.CHARACTERISTIC_VALUE: None,
              CHC.HEADER_INFO: None,
              CHC.PEAK_POSITION: None,}
    return config
