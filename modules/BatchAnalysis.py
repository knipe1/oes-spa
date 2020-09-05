#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Set up a dialog interface to analyze multiple spectra and extract
characteristic values for further applications.

Usage:
    from modules.BatchAnalysis import BatchAnalysis
    batch = BatchAnalysis(parent)  # parent as main window or application


Glossary:
    batchfile: The file in which the characteristic values are exported to.
    WDdirectory: Directory which is observed by the WatchDog (WD)


Created on Mon Jan 20 10:22:44 2020

@author: Hauke Wernecke
"""

# Method Sections:
    ### Properties
    ### Events
    ### Methods/Analysis
    ### UI-interactions
    ### Interaction with the FileSet self._files

# standard libs
import numpy as np
from datetime import datetime
from os.path import isdir

# third-party libs
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import QKeySequence as QKeys

# local modules/libs
from ConfigLoader import ConfigLoader
import modules.Universal as uni
import dialog_messages as dialog
from Logger import Logger
from modules.Spectrum import Spectrum
from ui.UIBatch import UIBatch
from modules.Watchdog import Watchdog
from modules.FileReader import FileReader
from modules.FileWriter import FileWriter
from modules.DataHandler import DataHandler


# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE
from custom_types.FileSet import FileSet
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC
from custom_types.BATCH_CONFIG import BATCH_CONFIG


class BatchAnalysis(QDialog):
    """
    Provides an interface to analyze multiple spectra.

    Provides a multiple file handling interface.
    May extract characteristic values for further applications.

    Usage:
        from modules.BatchAnalysis import BatchAnalysis
        batch = BatchAnalysis(parent)  # parent as main window or application

    Attributes
    ----------
    _batchfile : str
        The file to which the batch analysis is exported to.
    _updatePlots : bool
        Controls whether the plots are updated during the analysis.
    files : list
        Includes the files to analyze and display.
    lastdir : str
        Path of the last used directory to ease navigation.
    window :
        The ui.
    model : QStringListModel
        Object to handle the displayed files in the ui

    Methods
    -------
    specify_batchfile()
        Specifies the filename through a dialog.
    browse_spectra()
        Opens a dialog to browse for spectra and updates the filelist.
    multi_calc()
        Analyses the files and export the chracteristic values.
    retrieve_data(config:dict)
        Checks the config and retrieve the corresponing values from it.
    retrieve_batch_config()
        Gets the config of the analysis as base for further analysis.
    extract_values_of_config(config:dict, key:Enum)
        Extract the values of the given config with the specifc key.
    open_indexed_file(index)
        Retrieve the data of the selected file of the list.
    enable_analysis()
        Updates the UI according to the currently seleceted options.
    update_filelist(filelist:list)
        Updates the filelist and refreshes the ui.
    clear()
        Resets the filelist and clears the displayed files.
    update_progressbar(percentage:[int, float])
        Convert the percentage and sets the value to the progress bar.

    """

    # Load the configuration for batch analysis and export.
    config = ConfigLoader()
    BATCH = config.BATCH;
    EXPORT = config.EXPORT;


    ### Properties

    @property
    def batchFile(self):
        """batchFile getter"""
        return self._batchFile

    @batchFile.setter
    def batchFile(self, text:str):
        """batchFile setter: Updating the ui"""
        self._batchFile = text
        try:
            self.window.batchFile = text
        except:
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
        except:
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

        # Initialize the parent class ( == QDialog.__init__(self).
        super().__init__(parent)

        # Init the props to prevent errors in the ui-init routine.
        self.batchFile = None
        self.WDdirectory = None

        # Set up ui.
        self.window = UIBatch(self)

        # set up the logger
        self.logger = Logger(__name__)
        self.logger.info("Init BatchAnalysis")

        self.__post_init__()


    def __post_init__(self):
        # Set the defaults.
        self._files = FileSet(listWidget = self.window.listFiles,
                             updateOnChange = self.enable_analysis)
        self.batchFile = self.window.batchFile
        self.WDdirectory = self.window.WDdirectory
        self.dog = Watchdog()
        self.traceSpectrum = Spectrum(self.window.mplTrace, EXPORT_TYPE.BATCH)

        # Link events of the ui to methods of this class.
        self.set_connections()



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


    def deactivate_watchdog(self)->None:
        self.dog.stop()
        self.window.btnSetWatchdogDir.setEnabled(True)


    def activate_watchdog(self)->None:
        """
        Activates the WD if corresponding paths are valid.

        Returns
        -------
        None.

        """

        isValid = True
        # Prequerities given if WDpath and batchpath are defined.
        WDpath = self.WDdirectory
        if not isdir(WDpath):
            self.logger.warning("WDpath not defined: %s"%(WDpath))
            isValid = False

        batchPath = QFileInfo(self.batchFile).path()
        if not isdir(batchPath):
            self.logger.warning("batchPath not defined: %s"%(batchPath))
            isValid = False

        if not isValid:
            self.window.btnWatchdog.setChecked(False)
            return

        try:
            # Start WD for batchfile
            self.dog.start(WDpath, self.watchdog_event)

            # Start WD for spectra directory (if they differ).
            if not (WDpath == batchPath):
                self.dog.start(batchPath, self.watchdog_event)

            self.window.btnSetWatchdogDir.setEnabled(False)
        except AttributeError:
            self.logger.error("Error: No dog initialized!")


    def watchdog_event(self, path):
        self.logger.info("Watchdog: Modified file: %s"%(path))

        # Checks absolute paths to avoid issues due to relative vs absolute paths.
        batchPath = QFileInfo(self.batchFile).absoluteFilePath()
        eventPath = QFileInfo(path).absoluteFilePath()

        # Distinguish between modified batch- and spectrum-file.
        if batchPath == eventPath:
            self.logger.info("WD: Batchfile modified.")
            self.import_batch(takeCurrentBatchfile=True)
        else:
            self.logger.info("WD: Spectrum file modified/added.")
            self.update_filelist([eventPath])
            self._files.selectRowByFilename(eventPath)
            self.analyze(eventPath)



    def __repr__(self):
        info = {}
        info["batchfile"] = self.batchFile
        info["files"] = self._files
        info["lastdir"] = self.lastdir
        return self.__module__ + ":\n" + str(info)


    def set_connections(self):
        self.window.connect_browse_files(self.browse_spectra)
        self.window.connect_calculate(self.analyze)
        self.window.connect_cancel(self.set_cancel)
        self.window.connect_change_csvfile(self.enable_analysis)
        self.window.connect_clear(self.reset_files)
        self.window.connect_import_batch(self.import_batch)
        self.window.connect_select_file(self.open_indexed_file)
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
        print(self.batchFile)
        print(QFileInfo(self.batchFile).path())

        isFocused = self.window.focussed_filelist()
        isDelete = event.matches(QKeys.Delete)
        isCancel = event.matches(QKeys.Cancel)

        # Remove currently selected file.
        if isFocused and isDelete:
            row = self.window.listFiles.currentRow()
            self._files.remove(self._files[row])

        # Cancel current analysis
        if isCancel:
            self.set_cancel()


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
            if localUrl:
                valid_urls.add(localUrl)

        # Updates the filelist with the valid urls.
        self.update_filelist(valid_urls)


    ### Methods/Analysis

    # HACK: Single File
    def analyze(self, singleFile=None):
        self.logger.debug("Analyze file.")

        # Reset the properties to have a clean setup.
        self.cancelByEsc = False

        isSingleFile = bool(singleFile)
        if isSingleFile:
            singleFile = [singleFile]

        # Get the modus.
        isUpdatePlot = self.window.get_update_plots()
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
            if self.cancelByEsc:
                break

            # Update process bar
            self.window.update_progressbar((i+1)/amount)

            # Read out the filename and the data.
            file = files[i]
            self.currentFile = FileReader(file)

            if isExportBatch:
                # Get the data.
                specHandler = DataHandler(basicSetting)
                specHandler.analyse_data(self.currentFile)
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

                config = self.retrieve_batch_config()
                config[CHC.BASELINE] = avg
                config[CHC.CHARACTERISTIC_VALUE] = characteristicValue
                config[CHC.PEAK_AREA] = peakArea
                config[CHC.PEAK_HEIGHT] = peakHeight
                config[CHC.PEAK_POSITION] = peakPosition
                # Convert to string for proper presentation.
                config[CHC.HEADER_INFO] = uni.timestamp_to_string(timestamp)

                data.append(self.assemble_row(file, config))
                # HACK: ----------------------------------------------------------
                if isSingleFile:
                    self.export_batch(self.assemble_row(file, config), singleLine=True)
                # HACK: ----------------------------------------------------------

            # Select by filename to trigger event based update of the plot.
            if isUpdatePlot and not isSingleFile:
                self._files.selectRowByFilename(file)

        if isExportBatch and not isSingleFile:
            # Get the name of the peak for proper description.
            characteristicName = basicSetting.fitting.currentPeak.name
            peakName = CHC.CHARACTERISTIC_VALUE.value + " (%s)"%(characteristicName)
            self.export_batch(data, peakName=peakName)

        if isPlotTrace:
            self.import_batch(takeCurrentBatchfile=True)


        # Prompt the user with information about the skipped files.
        if not isSingleFile:
            dialog.information_BatchAnalysisFinished(skippedFiles)


    # TODO: Do not uses self --> can be static or out of the class
    def get_timediff_H(self, spectrum, timestamp):
        try:
            refTime = spectrum.referenceTime
        except:
            refTime = timestamp
            spectrum.referenceTime = refTime

        diffTime = uni.convert_to_hours(timestamp - refTime)

        return diffTime


    def import_batch(self, takeCurrentBatchfile=False):

        # Define the specific value which shall be plotted.
        # TODO: rename to currentTraceValue
        columnValue = self.window.currentTrace

        # Select the file from which the data shall be imported.
        try:
            if not takeCurrentBatchfile:
                file = dialog.dialog_openFiles(self.lastdir, singleFile=True)
                self.currentFile = FileReader(file, columnValue=columnValue)
                # Change interface and preset for further dialogs (lastdir)
                path = QFileInfo(file).path()
                self.lastdir = path
            else:
                # Reload the data with new characteristica.
                self.currentFile = FileReader(self.window.batchFile,
                                              columnValue=columnValue)
        except:
            # Could not get a file.
            self.logger.error("Import Batch: Could not get a file.")
            return -10

        # Retrieve data.
        try:
            # TODO: Check sorting of 2D arrays make sense here.
            timestamps, values = self.currentFile.data
            diffTimes = np.zeros((len(timestamps,)))

            for idx, timestamp in enumerate(timestamps):
                diffTime = self.get_timediff_H(self.traceSpectrum, timestamp)
                diffTimes[idx] = diffTime
        except:
            # Could not retrieve valid data.
            self.logger.error("Import Batch: Could not retrieve valid data.")
            return -20

        # Plot the trace.
        try:
            self.traceSpectrum.init_plot()
            self.traceSpectrum.update_data(diffTimes, values)
            self.traceSpectrum.set_y_label(columnValue)
            self.traceSpectrum.update_plot()
        except:
            # Could not retrieve valid data.
            self.logger.error("Import Batch: Could not plot data.")
            return -30

        return 0


    def export_batch(self, data, peakName=None, singleLine=False):

        # Assemble header with the name of the characteristic value.
        header = self.assemble_header(valueName=peakName)

        # Export in csv file.
        csvWriter = FileWriter(self.batchFile)
        if singleLine:
            csvWriter.write_line(data)
        else:
            csvWriter.write_data(data, header, EXPORT_TYPE.BATCH)


    def assemble_header(self, valueName=""):
        # TODO: check magic string?
        # TODO: Check for an extra config entry to add the "Filename" dynamically
        config = self.retrieve_batch_config()

        header = ["Filename"]
        header += [label.value for label in config.keys()]

        # Replace 'Characteristic value' with proper name.
        try:
            idx = header.index(CHC.CHARACTERISTIC_VALUE.value)
            header[idx] = valueName
        except ValueError:
            self.logger.warning("No export of characteristic values.")

        return header


    def assemble_row(self, filename, config):
        # TODO: pure file? Not reduced path nor indexed?
        row = [filename]
        row += [value for value in config.values()]
        return row


    def retrieve_batch_config(self):
        """
        Gets the plain config for analysis.

        Provides the config in a dict to loop through in other methods.

        Returns
        -------
        config: dict
            Containts the CHARACTERISTIC enum as dict with default values.

        """

        config = {CHC.PEAK_HEIGHT: None,
                  CHC.PEAK_AREA: None,
                  CHC.BASELINE: None,
                  CHC.CHARACTERISTIC_VALUE: None,
                  CHC.HEADER_INFO: None,
                  CHC.PEAK_POSITION: None,}
        return config


    ### UI-interactions


    def specify_batchfile(self):
        """
        Specifies the filename through a dialog.

        Determines the batchfile, updates the lastdir-prop, updates the ui.
        Linked to ui button.

        Returns
        -------
        filename : str
            The filename selected by the user.
            None if dialog was quit or cancelled.

        """

        # Retrieve the filename and the corresponding info
        filename = dialog.dialog_saveFile(self.lastdir,  parent=self)

        # Cancel or quit the dialog.
        if not filename:
            return None

        # TODO: validation in add_suffix? Use try-except then.
        filename, path = uni.add_suffix(filename, self.BATCH["SUFFIX"])

        # Change interface and preset for further dialogs (lastdir)
        self.lastdir = path
        self.batchFile = filename

        return filename


    def specify_watchdog_directory(self):
        directory = dialog.dialog_getDirectory(self.lastdir)

        # TODO: Use property here?! Liek batchFile
        self.WDdirectory = directory
        self.window.WDdirectory = directory

        # Update last directory if not cancelled.
        if directory:
            self.lastdir = directory




    def browse_spectra(self):
        """Opens a dialog to browse for spectra and updates the filelist."""
        filelist = dialog.dialog_openFiles(self.lastdir)
        self.update_filelist(filelist)
        try:
            url = filelist[0]
            path = QFileInfo(url).path()
            self.lastdir = path
        except:
            print(filelist)
            self.logger.info("Browse Spectra: Could not update directory.")


    def enable_analysis(self):
        """
        Updates the UI according to the currently selected options.

        Set Filename, Browse, Clear, and Parameters are always available.
        Availability of Calculate depends on the former elements.

        Returns
        -------
        enable : bool
            The current status of the button "Calculate" (btnCalculate).

        """
        enable = True;

        # Check for specified batchFile, selected files, and ticked parameters.
        if not self.batchFile:
            enable = False
        if not self._files:
            enable = False

        self.window.enable_analysis(enable)

        return enable


    def open_indexed_file(self, index):
        """
        Retrieve the data of the selected file of the list.

        Used for applying the data after clicking on the list.

        Parameters
        ----------
        index : QModelIndex or int
            Transmitted by the list. Or programmatically.

        Returns
        -------
        None.

        """

        # TODO: Errorhandling?
        # Distinguish given index by numerical value (from another method) or
        # is given by the ListModel (by an event)
        try:
            index = index.row()
        except AttributeError:
            print("Open indexed file called programmatically")

        try:
            self.parent().apply_data(self._files[index])
        except IndexError:
            print("Invlaid index. Could not open file of index ", index)



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
        self._files.update(filelist)
        self.logger.debug("Filelist updated.")


    def reset_files(self):
        """Resets the filelist."""
        self._files.clear()


    def set_cancel(self):
        """Demands a cancellation. Processed in corresponing methods."""
        self.cancelByEsc = True
