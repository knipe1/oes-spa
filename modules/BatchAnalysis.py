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
from PyQt5.QtCore import QFileInfo, QModelIndex
from PyQt5.QtWidgets import QDialog

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

    # HACK: ABort the calculation
        self.window.connect_cancel(self.set_cancel)


    def set_cancel(self):
        self.cancelByEsc = True

    ### Events
    ### UI-interactions


    # HACK ------------------------------------------------------------
    def keyPressEvent(self, event):
        from PyQt5.QtGui import QKeySequence
        isFocused = self.window.listFiles.hasFocus()
        isDelete = event.matches(QKeySequence.Delete)
        if isFocused and isDelete:
            row = self.window.listFiles.currentRow()
            self._files.remove(self._files[row])

        isCancel = event.matches(QKeySequence.Cancel)
        if isCancel:
            self.set_cancel()
    # HACK ------------------------------------------------------------


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
        self.concentrationSpectrum = Spectrum(
                self.window.mplConcentration, EXPORT_TYPE.BATCH)
        # Get the modus.
        isUpdatePlot = self.window.get_update_plots()
        isPlotConcentration = self.window.get_plot_concentration()
        isExportBatch = self.window.get_export_batch()
        # Get characteristic values.
        basicSetting = self.parent().window.get_basic_setting()

        data = []
        skippedFiles = []
        files = self._files.to_list()
        amount = len(files)

        for i in range(amount):
            # HACK: Works only if event queue is flushed, like when redrawing
            # a plot. But do not work during "just" exporting.
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
            elif isPlotConcentration:
                # TODO: currently just peakArea, no dropdown.
                data = (timestamp, peakArea)
                self.import_batch(data)

        if isExportBatch:
            characteristicName = basicSetting.fitting.currentPeak.name
            self.export_batch(data, peakName=characteristicName)

        # Prompt the user with information about the skipped files.
        dialog.information_BatchAnalysisFinished(skippedFiles)


    def plot_concentration(self, timestamp, value):
        # TODO: To be tested.
        # Get the timediff of the spectrum in h.
        diffTime = self.get_timediff_H(self.concentrationSpectrum,
                                          timestamp)

        self.concentrationSpectrum.update_data(diffTime, value)
        self.concentrationSpectrum.init_plot()
        self.concentrationSpectrum.update_plot()


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

            diffTimes = self.get_timediff_H(self.concentrationSpectrum,
                                              timestamp)

        except:
            diffTimes = []

            self.concentrationSpectrum = Spectrum(
                    self.window.mplConcentration, EXPORT_TYPE.BATCH)

            filelist = dialog.dialog_openFiles(self.lastdir)
            file = filelist[0]
            self.currentFile = FileReader(file)


            data = self.currentFile.data

            timestamps, values = data

            for timestamp in timestamps:
                diffTime = self.get_timediff_H(self.concentrationSpectrum,
                                                  timestamp)
                diffTimes.append(diffTime)

        self.concentrationSpectrum.update_data(diffTimes, values)
        self.concentrationSpectrum.init_plot()
        self.concentrationSpectrum.update_plot()


    def export_batch(self, data, peakName=None):

        # Assemble header with the name of the characteristic value.
        header = self.assemble_header(valueName=peakName)

        # Export in csv file.
        csvWriter = FileWriter(self.batchFile)
        csvWriter.write_data(data, header, EXPORT_TYPE.BATCH)

    # def multi_calc(self):
    #     """
    #     Analyses the files and export the charcteristic values.

    #     Returns
    #     -------
    #     None.

    #     """

    #     # TODO: any kind of errorhandling?
    #     # Wrong format for the timestamp?
    #     # cannot found batchfile? If empty for example?
    #     # validate successful export?


    #     # Get characteristic values.
    #     basicSetting = self.parent().window.get_basic_setting()
    #     characteristicName = basicSetting.fitting.currentPeak.name

    #     # HINT: EXPORT
    #     # Assemble header with the name of the characteristic value.
    #     header = self.assemble_header(valueName=characteristicName)

    #     # Separate the valid data from skipped files.
    #     data, skippedFiles = self.retrieve_data(basicSetting)

    #     # HINT: EXPORT
    #     # Export in csv file.
    #     csvWriter = FileWriter(self.batchFile)
    #     csvWriter.write_data(data, header, EXPORT_TYPE.BATCH)

    #     # prompt the user with information about the skipped files
    #     dialog.information_BatchAnalysisFinished(skippedFiles)


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


    # def retrieve_data(self, basicSetting):
    #     """
    #     Checks the config and retrieve the corresponing values from it.

    #     Loops through the files and get the data. Optional it will also update
    #     the plots.

    #     Parameters
    #     ----------
    #     config : dict
    #         The dict of the configuration.

    #     Returns
    #     -------
    #     data : list of lists
    #         Contains the data of the files in a matrix.
    #     skippedFiles : list
    #         Including filenames of the skipped files due to invalid data.

    #     """
    #     # TODO: errorhandling

    #     # lists for data of valid files and the skipped files due not fitting
    #     # the format, e.g. other csv files
    #     self.cancelByEsc = False

    #     data = []
    #     skippedFiles = []
    #     files = self._files.to_list()
    #     config = self.retrieve_batch_config()
    #     amount = len(files)

    #     for i in range(amount):
    #         if self.cancelByEsc:
    #             break

    #         # Update process bar
    #         self.window.update_progressbar((i+1)/amount)

    #         # Read out the filename and the data.
    #         file = files[i]
    #         self.currentFile = FileReader(file)

    #         # Skip the file if data is invalid.
    #         if not self.currentFile.is_valid_datafile():
    #             skippedFiles.append(file)
    #             continue

    #         # Get the data.
    #         specHandler = DataHandler(basicSetting)
    #         results = specHandler.analyse_data(self.currentFile)
    #         avg = specHandler.avgbase
    #         peakHeight = specHandler.peakHeight
    #         peakArea = specHandler.peakArea
    #         peakPosition = specHandler.peakPosition
    #         characteristicValue = specHandler.characteristicValue
    #         timestamp = self.currentFile.timestamp

    #         # excluding file if no appropiate data given like in processed
    #         # spectra.
    #         # TODO: Check more exlude conditions like characteristic value
    #         # below some defined threshold.
    #         # TODO: validate_results as method of specHandlaer? Would also omit
    #         # the assignemts above!?
    #         if not peakHeight:
    #             skippedFiles.append(file)
    #             continue

    #         config[CHARAC.BASELINE] = avg
    #         config[CHARAC.CHARACTERISTIC_VALUE] = characteristicValue
    #         config[CHARAC.PEAK_AREA] = peakArea
    #         config[CHARAC.PEAK_HEIGHT] = peakHeight
    #         config[CHARAC.PEAK_POSITION] = peakPosition
    #         # TODO: Check HEADER_INFO is just timestamp?
    #         config[CHARAC.HEADER_INFO] = uni.timestamp_to_string(timestamp)

    #         # assembling the row and appending it to the data
    #         # TODO: pure file? Not reduced path nor indexed?
    #         row = [file]
    #         row += [value for value in config.values()]
    #         data.append(row)


    #         # HACK: If this analysis should run in a thread, it would be easier
    #         # to generate a new window and display eventually the rawData
    #         # and the peakArea-time-graph in another plot.
    #         # Update the plots.
    #         if self.window.get_update_plots():
    #             self.parent().apply_data(file)
    #         # Update the concentration plot.
    #         elif self.window.get_plot_concentration():
    #             # Get the reference time once and then always the difference.
    #             if not i:
    #                 concentrationSpectrum = Spectrum(
    #                     self.window.mplConcentration, EXPORT_TYPE.BATCH)
    #                 refTime = timestamp
    #             # Convert to hours. See also configuration of the plot.
    #             diffTime = uni.convert_to_hours(timestamp - refTime)

    #             concentrationSpectrum.update_data(diffTime, peakArea)
    #             concentrationSpectrum.init_plot()
    #             concentrationSpectrum.update_plot()

    #     return data, skippedFiles


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


    # def extract_values_of_config(self, config:dict, key):
    #     """
    #     Extract the values of the given config with the specifc key.

    #     If the config contains a key, value pair with {"status": True}.

    #     Parameters
    #     ----------
    #     config : dict
    #         A dict that must contain the given key and the key "status".
    #     key : string
    #         Key to retrieve the specific value of all items of the config.

    #     Returns
    #     -------
    #     list
    #         Contains all items of the specific key. Empty if "status"-key does
    #         not exist in config.

    #     """

    #     data = []

    #     # Append value if the checkbox is ticked.
    #     for _, item in config.items():
    #         if item.get(BATCH_CONFIG.STATUS):
    #             data.append(item[key])

    #     return data;


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
            print("Invlaid index. Could not open file of index " + str(index))



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




##############################################################################
# HACK TEST AREA