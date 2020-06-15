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
from modules.FileReader import FileReader
from modules.FileWriter import FileWriter
from modules.DataHandler import DataHandler


# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE
from custom_types.FileSet import FileSet
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHARAC
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

    # Set up the logger.
    logger = Logger(__name__)


    ### Properties

    @property
    def batchFile(self):
        """batchFile getter"""
        return self._batchFile

    @batchFile.setter
    def batchFile(self, text:str):
        """batchFile setter: Updating the ui"""
        self._batchFile = text
        self.window.batchFile = text


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

        self.logger.info("Init BatchAnalysis")

        # Initialize the parent class ( == QDialog.__init__(self).
        super().__init__(parent)

        # Set up ui.
        self.window = UIBatch(self)

        self.__post_init__()


    def __post_init__(self):
        # Set the defaults.
        self._files = FileSet(listWidget = self.window.listFiles,
                             updateOnChange = self.enable_analysis)
        self.batchFile = self.window.batchFile

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
        self.window.connect_cancel(self.set_cancel)
        self.window.connect_change_csvfile(self.enable_analysis)
        self.window.connect_clear(self.reset_files)
        self.window.connect_import_batch(self.import_batch)
        self.window.connect_select_file(self.open_indexed_file)
        self.window.connect_set_filename(self.specify_batchfile)



    ### Events
    ### UI-interactions


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
            if uni.is_valid_filetype(url):
                valid_urls.add(url.toLocalFile())

        # Updates the filelist with the valid urls.
        self.update_filelist(valid_urls)


    ### Methods/Analysis

    def analyze(self):

        # Reset the properties to have clean setup.
        self.cancelByEsc = False
        self.traceSpectrum = Spectrum(
                self.window.mplTrace, EXPORT_TYPE.BATCH)
        # Get the modus.
        isUpdatePlot = self.window.get_update_plots()
        isPlotTrace = self.window.get_plot_trace()
        isExportBatch = self.window.get_export_batch()
        # Get characteristic values.
        basicSetting = self.parent().window.get_basic_setting()

        data = []
        skippedFiles = []
        files = self._files.to_list()
        amount = len(files)

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

            # Get the data.
            specHandler = DataHandler(basicSetting)
            results = specHandler.analyse_data(self.currentFile)
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

            if isExportBatch:
                config = self.retrieve_batch_config()
                config[CHARAC.BASELINE] = avg
                config[CHARAC.CHARACTERISTIC_VALUE] = characteristicValue
                config[CHARAC.PEAK_AREA] = peakArea
                config[CHARAC.PEAK_HEIGHT] = peakHeight
                config[CHARAC.PEAK_POSITION] = peakPosition
                # TODO: Check HEADER_INFO is just timestamp?
                config[CHARAC.HEADER_INFO] = uni.timestamp_to_string(timestamp)

                data.append(self.assemble_row(file, config))
            elif isUpdatePlot:
                self.parent().apply_data(file)
            elif isPlotTrace:
                # TODO: currently just peakArea, no dropdown.
                data = (timestamp, peakArea)
                self.import_batch(data)

        if isExportBatch:
            characteristicName = basicSetting.fitting.currentPeak.name
            self.export_batch(data, peakName=characteristicName)

        # Prompt the user with information about the skipped files.
        dialog.information_BatchAnalysisFinished(skippedFiles)


    def plot_trace(self, timestamp, value):
        # TODO: To be tested.
        # Get the timediff of the spectrum in h.
        diffTime = self.get_timediff_H(self.traceSpectrum,
                                          timestamp)

        self.traceSpectrum.update_data(diffTime, value)
        self.traceSpectrum.init_plot()
        self.traceSpectrum.update_plot()


    def get_timediff_H(self, spectrum, timestamp):
        try:
            refTime = spectrum.referenceTime
        except:
            refTime = timestamp
            spectrum.referenceTime = refTime


        diffTime = uni.convert_to_hours(timestamp - refTime)

        return diffTime

    def import_batch(self, data=None):


        try:
            timestamp, values = data

            diffTimes = self.get_timediff_H(self.traceSpectrum,
                                              timestamp)

        except:
            diffTimes = []

            self.traceSpectrum = Spectrum(
                    self.window.mplTrace, EXPORT_TYPE.BATCH)

            filelist = dialog.dialog_openFiles(self.lastdir)
            # TODO: Issue if cancelled
            file = filelist[0]
            self.currentFile = FileReader(file)


            data = self.currentFile.data

            timestamps, values = data

            for timestamp in timestamps:
                diffTime = self.get_timediff_H(self.traceSpectrum,
                                                  timestamp)
                diffTimes.append(diffTime)

        self.traceSpectrum.update_data(diffTimes, values)
        self.traceSpectrum.init_plot()
        self.traceSpectrum.update_plot()


    def export_batch(self, data, peakName=None):

        # Assemble header with the name of the characteristic value.
        header = self.assemble_header(valueName=peakName)

        # Export in csv file.
        csvWriter = FileWriter(self.batchFile)
        csvWriter.write_data(data, header, EXPORT_TYPE.BATCH)


    def assemble_header(self, valueName=""):
        # TODO: check magic string?
        # TODO: Check for an extra config entry to add the "Filename" dynamically
        config = self.retrieve_batch_config()

        header = ["Filename"]
        header += [label.value for label in config.keys()]

        # Replace 'Characteristic value' with proper name.
        try:
            idx = header.index(CHARAC.CHARACTERISTIC_VALUE.value)
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

        config = {CHARAC.PEAK_HEIGHT: None,
                  CHARAC.PEAK_AREA: None,
                  CHARAC.BASELINE: None,
                  CHARAC.CHARACTERISTIC_VALUE: None,
                  CHARAC.HEADER_INFO: None,
                  CHARAC.PEAK_POSITION: None,}
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
        # is given by the ListModel (by an click event)
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


    def reset_files(self):
        """Resets the filelist."""
        self._files.clear()


    def set_cancel(self):
        """Demands a cancellation. Processed in corresponing methods."""
        self.cancelByEsc = True
