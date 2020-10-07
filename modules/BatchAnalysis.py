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
from PyQt5.QtCore import QFileInfo
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
from modules.Spectrum import Spectrum
from modules.Watchdog import Watchdog
from modules.FileReader import FileReader
from modules.BatchWriter import BatchWriter
from modules.SpectrumHandler import SpectrumHandler


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
        self.window.connect_import_batch(self.import_batch)
        self.window.connect_select_file(self.open_indexed_file)
        self.window.connect_select_file(self.enable_analysis)
        self.window.connect_set_filename(self.specify_batchfile)
        self.window.connect_change_trace(self.import_batch)
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


    def dropEvent(self, event):
        """
        Filter the dropped urls to update the files with only valid urls.

        Parameters
        ----------
        event : event
            The event itself.

        Returns
        -------
        None.

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
        except KeyError:
            self.logger.debug("No invalid url found.")

        # Updates the filelist with the valid urls.
        self.update_filelist(valid_urls)


    ### Watchdog routines

    def watchdog_event_handler(self, path:str)->None:
        # Checks absolute paths to avoid issues due to relative vs absolute paths.
        eventPath, _ = uni.extract_path_and_basename(path)

        # Distinguish between modified batch- and spectrum-file.
        if self.batchFile == path:
            self.logger.info("WD: Batchfile modified.")
            self.import_batch(takeCurrentBatchfile=True)
        elif self.WDdirectory == eventPath:
            self.logger.info("WD: Spectrum file modified/added: %s"%(path))
            errorcode = self.analyze(path)
            if not errorcode ==ERR.OK:
                return
            self.update_filelist([path])
            self._files.select_row_by_filename(path)


    def toggle_watchdog(self, status:bool)->None:
        """
        Activates or deactivates the Watchdog.


        Parameters
        ----------
        status : bool
            Activates the WD if True, deactivates otherwise.

        Returns
        -------
        None.

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
        self.logger.debug("Analyze file.")

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

            # Be responsive and process events to enable cancelation.
            QApplication.processEvents()
            if self.isScheduledCancel:
                break

            # Update process bar
            self.window.update_progressbar((i+1)/amount)

            # Read out the filename and the data.
            file = files[i]
            self.currentFile = FileReader(file)

            if isExportBatch:
                # Get the data.
                specHandler = SpectrumHandler(basicSetting)
                errorcode = specHandler.analyse_data(self.currentFile)
                if not errorcode == ERR.OK:
                    return errorcode

                avg = specHandler.avgbase
                peakHeight = specHandler.peakHeight
                peakArea = specHandler.peakArea
                peakPosition = specHandler.peakPosition
                characteristicValue = specHandler.characteristicValue
                timestamp = self.currentFile.timestamp

                # excluding file if no appropiate data given like in processed
                # spectra.
                # TODO: Check more exlude conditions like characteristic value
                # below some defined threshold.
                # TODO: validate_results as method of specHandlaer? Would also omit
                # the assignemts above!?
                if not peakHeight:
                    skippedFiles.append(file)
                    continue

                config = retrieve_batch_config()
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
                self.export_batch(data, header, isUpdate=True)
            else:
                self.export_batch(data, header)

        if isPlotTrace:
            self.import_batch(takeCurrentBatchfile=True)


        # Prompt the user with information about the skipped files.
        if not isSingleFile:
            dialog.information_BatchAnalysisFinished(skippedFiles)

        return ERR.OK



    def import_batch(self, takeCurrentBatchfile=False):
        # Define the specific value which shall be plotted.
        columnValue = self.window.currentTraceValue

        # Select the file from which the data shall be imported.
        filename = self.determine_batchfile(takeCurrentBatchfile)
        if not filename:
            return

        file = FileReader(filename, columnValue=columnValue)
        if file.is_valid_spectrum() == ERR.OK:
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
            filename = dialog.dialog_openBatchFile(self.lastdir)
            self.lastdir = filename
        return filename


    def calculate_time_differences(self, timestamps):
        diffTimes = np.zeros((len(timestamps),))

        for idx, timestamp in enumerate(timestamps):
            diffTime = self.traceSpectrum.get_timediff_H(timestamp)
            diffTimes[idx] = diffTime
        return diffTimes


    def export_batch(self, data, header, isUpdate=False):

        # Export in csv file.
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
        filename = dialog.dialog_saveBatchfile(self.lastdir)

        # Cancel or quit the dialog.
        if not filename:
            return

        filename = uni.replace_suffix(filename)

        # Change interface and preset for further dialogs (lastdir)
        self.lastdir = filename
        self.batchFile = filename

        return filename


    def specify_watchdog_directory(self):
        directory = dialog.dialog_getWatchdogDirectory(self.lastdir)

        if directory:
            self.WDdirectory = directory
            self.lastdir = directory



    def browse_spectra(self):
        """Opens a dialog to browse for spectra and updates the filelist."""
        filelist = dialog.dialog_openSpectra(self.lastdir)
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


    def open_indexed_file(self, index):
        """
        Retrieve the data of the selected file of the list.

        Used for applying the data after clicking on the list.

        Parameters
        ----------
        index : QModelIndex or int
            Transmitted by the list. Or programmatically.

        """

        # Distinguish given index by numerical value (from another method) or
        # is given by the ListModel (by an event)
        try:
            index = index.row()
        except AttributeError:
            self.logger.debug("Open indexed file called programmatically.")

        try:
            self.parent().apply_data(self._files[index])
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
