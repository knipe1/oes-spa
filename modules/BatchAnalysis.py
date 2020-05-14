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
    ### Interaction with the FileSet self.files

# standard libs
import numpy as np
import threading as THR

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
    retrieve_data(dictionary:dict)
        Checks the config and retrieve the corresponing values from it.
    retrieve_batch_config()
        Gets the config of the analysis as base for further analysis.
    extract_values_of_config(dictionary:dict, key:Enum)
        Extract the values of the given dictionary with the specifc key.
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

    # set up the logger
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
        # self.window.set_batchfile(text)
        # self.enable_analysis()



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

        # TODO: check whether there will be some inconsistency if self.lastdir
        # is set or if it even useful to implement it like this.
        self.lastdir = parent.lastdir

        # General settings.
        self.setAcceptDrops(True)
        # self.model = QStringListModel()
        # init of window has to be at last, because it connects self.model i.a.
        self.window = UIBatch(self)

        self.__post_init__()


    def __post_init__(self):
        # Set the defaults.
        self.files = FileSet(listWidget = self.window.listFiles,
                             updateOnChange = self.enable_analysis)
        self.batchFile = self.window.batchFile



    ### Events
    ### UI-interactions


    # HACK ------------------------------------------------------------
    def keyPressEvent(self, event):
        from PyQt5.QtGui import QKeySequence
        isFocused = self.window.listFiles.hasFocus()
        isDelete = event.matches(QKeySequence.Delete)
        if isFocused and isDelete:
            row = self.window.listFiles.currentRow()
            self.files.remove(self.files[row])
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
        valid_urls = []

        # Get the urls and check their validity.
        urls = event.mimeData().urls();
        for url in urls:
            if uni.is_valid_filetype(url):
                valid_urls.append(url.toLocalFile())

        # Updates the filelist with the valid urls.
        self.update_filelist(valid_urls)


    ### Methods/Analysis

    # TEST ---------------------------------------------------------------
    def multi_calc(self):
        # test = THR.Thread(target=self.multi_calc_thread)
        # test.start()
        self.multi_calc_thread()
    # TEST ---------------------------------------------------------------

    def multi_calc_thread(self):
        """
        Analyses the files and export the chracteristic values.

        Returns
        -------
        None.

        """

        # TODO: any kind of errorhandling?
        # Wrong format for the timestamp?
        # cannot found batchfile? If empty for example?
        # validate successful export?


        # Get characteristic values.
        basicSetting = self.parent().window.get_basic_setting()
        characteristicName = basicSetting.fitting.currentPeak.name

        # Load the dictionary for processing the data.
        batchConfig = self.retrieve_batch_config();


        # Assemble header by extracting all labels of the config.
        header = self.assemble_header(batchConfig, valueName=characteristicName)

        # Separate the valid data from skipped files.
        data, skippedFiles = self.retrieve_data(batchConfig, basicSetting)

        # export in csv file
        csvWriter = FileWriter(self.batchFile)
        csvWriter.write_data(data, header, EXPORT_TYPE.BATCH)

        # prompt the user with information about the skipped files
        dialog.information_BatchAnalysisFinished(skippedFiles)


    def assemble_header(self, config, valueName=""):
        # TODO: check magic string?
        header = ["Filename"]
        enumLabels = self.extract_values_of_config(config, BATCH_CONFIG.LABEL)
        header += [label.value for label in enumLabels]

        # HACK?
        # Replace 'Characteristic value' with proper name
        hasCharacteristicValue = header.count(CHARAC.CHARACTERISTIC_VALUE.value)
        if hasCharacteristicValue:
            idx = header.index(CHARAC.CHARACTERISTIC_VALUE.value)
            header[idx] = valueName

        return header


    def retrieve_data(self, dictionary:dict, basicSetting):
        """
        Checks the config and retrieve the corresponing values from it.

        Loops through the files and get the data. Optional it will also update
        the plots.

        Parameters
        ----------
        dictionary : dict
            The dict of the configuration.

        Returns
        -------
        data : list of lists
            Contains the data of the files in a matrix.
        skippedFiles : list
            Including filenames of the skipped files due to invalid data.

        """
        # TODO: errorhandling

        # lists for data of valid files and the skipped files due not fitting
        # the format, e.g. other csv files
        data = []
        skippedFiles = []
        amount = len(self.files)


        #### HACK ####################################################
        from datetime import datetime
        concentrationSpectrum = Spectrum(self.window.mplConcentration, EXPORT_TYPE.BATCH)
        xxxData = []
        yyyData = []
        difference = []
        # self.window.mplConcentration.axes.clear()
        #### HACK ####################################################

        for i in range(amount):
            # Update process bar
            self.window.update_progressbar((i+1)/amount)

            # Read out the file
            file = self.files[i]
            self.currentFile = FileReader(file)

            # Skip the file if data is invalid.
            if not self.currentFile.is_valid_datafile():
                skippedFiles.append(file)
                continue

            # HACK: If this analysis should run in a thread, it would be easier
            # to generate a new window and display eventually the rawData
            # and the peakArea-time-graph in another plot.
            # Update the plots.
            if self.window.get_update_plots():
                # HINT: There is a dialog shown when the file contains invalid data.
                self.parent().apply_data(file)


            xData, yData = self.currentFile.data
            timestamp = self.currentFile.timestamp
            # timestamp = datetime.strptime(timestamp,
            #                               self.EXPORT["FORMAT_TIMESTAMP"])

            specHandler = DataHandler(basicSetting)
            results = specHandler.analyse_data(self.currentFile)
            avg = specHandler.avgbase
            peakHeight = specHandler.peakHeight
            peakArea = specHandler.peakArea
            peakPosition = specHandler.peakPosition
            characteristicValue = specHandler.characteristicValue

            # excluding file if no appropiate data given like in processed spectra
            # TODO: Check more exlude conditions like characteristic value
            # below some defined threshold
            # TODO: validate_results as method of specHandlaer?
            if not peakHeight:
                skippedFiles.append(file)
                continue

            # link values to dicts
            # If the list of characteristics gets larger, a loop is possible by
            # assigning a dict (works as a reference) to the value, e.g.:
            # peakHeight = {}
            # dictionary[CHARAC.PEAK_HEIGHT.value]["value"] = peakHeight
            # peakHeight["numerical value"] = xy
            # TODO: is dict.get() useful here? get allows a default value,
            # and will not raise a KeyError
            # see therefore: https://stackoverflow.com/questions/11041405/why-dict-getkey-instead-of-dictkey
            dictionary[CHARAC.PEAK_HEIGHT][BATCH_CONFIG.VALUE] = peakHeight
            dictionary[CHARAC.PEAK_AREA][BATCH_CONFIG.VALUE] = peakArea
            dictionary[CHARAC.BASELINE][BATCH_CONFIG.VALUE] = avg
            # TODO: Check HEADER_INFO is just timestamp?
            dictionary[CHARAC.HEADER_INFO][BATCH_CONFIG.VALUE] = timestamp
            dictionary[CHARAC.PEAK_POSITION][BATCH_CONFIG.VALUE] = peakPosition
            dictionary[CHARAC.CHARACTERISTIC_VALUE][BATCH_CONFIG.VALUE] = characteristicValue

            # assembling the row and appending it to the data
            # TODO: pure file? Not reduced path or indexed?
            row = [file]
            row += self.extract_values_of_config(dictionary, BATCH_CONFIG.VALUE)
            data.append(row)

            #### HACK ####################################################
            yyyData.append(peakArea)
            xxxData.append(timestamp)

            # time_0 = xxxData[0]

            # TODO: Change to minutes? hours?
            # difference.append((time - time_0).seconds)
            concentrationSpectrum.update_data(xxxData, yyyData)
            # concentrationSpectrum.update_data(difference, yyyData)
            concentrationSpectrum.init_plot()
            concentrationSpectrum.update_plot()
        #### HACK ####################################################

        return data, skippedFiles


    def retrieve_batch_config(self):
        """
        Gets the config of the analysis as base for further analysis.

        Provides the config in a dictionary to loop through in other methods.

        Raises
        ------
        ValueError
            Raises when the config is not acceptable.

        Returns
        -------
        properties: dict
            Includes the ui elements and the matching labels.

        """

        # TODO: errorhandling
        defValue = 0   # Should be falsy to skip file by default.
        properties = {}

        # make sure this is in the correct order that they match to the loop
        # of self.window.BtnParameters.buttons()
        labels = [CHARAC.PEAK_HEIGHT,
                  CHARAC.PEAK_AREA,
                  CHARAC.BASELINE,
                  CHARAC.CHARACTERISTIC_VALUE,
                  CHARAC.HEADER_INFO,
                  CHARAC.PEAK_POSITION,]

        # Retrieve checkboxes and their properties.
        checkboxes = [{BATCH_CONFIG.CHECKBOX: cb,
                       BATCH_CONFIG.NAME: cb.objectName(),
                       BATCH_CONFIG.STATUS: cb.isChecked(),
                       BATCH_CONFIG.VALUE: defValue,
                       } for cb in self.window.BtnParameters.buttons()]

        # Errorhandling
        if len(checkboxes) != len(labels):
            raise ValueError("""Checkboxes and labels are not fitting!
                             Please check configuration""")

        # Union labels and checkboxes.
        for checkbox, label in zip(checkboxes, labels):
            # Add the label-key and the corresponding value to the indiviual
            # setting.
            checkbox.update({BATCH_CONFIG.LABEL: label})
            # Add the individual setting and merge it to the complete setting.
            properties[checkbox[BATCH_CONFIG.LABEL]] = checkbox

        return properties;


    def extract_values_of_config(self, config:dict, key):
        """
        Extract the values of the given dictionary with the specifc key.

        If the dictionary contains a key, value pair with {"status": True}.

        Parameters
        ----------
        dictionary : dict
            A dict that must contain the given key and the key "status".
        key : string
            Key to retrieve the specific value of all items of the dictionary.

        Returns
        -------
        list
            Contains all items of the specific key. Empty if "status"-key does
            not exist in dictionary.

        """

        data = []

        # Append value if the checkbox is ticked.
        for _, item in config.items():
            if item.get(BATCH_CONFIG.STATUS):
                data.append(item[key])

        return data;


    ### UI-interactions


    def specify_batchfile(self):
        """
        Specifies the filename through a dialog.

        Determines the batchfile, updates the lastdir-prop, updates the ui.
        NO setter function.
        Linked to ui button.

        Returns
        -------
        filename : str
            The filename selected by the user. Empty string if dialog was
            quit or cancelled.

        """

        # Retrieve the filename and the corresponding info
        filename = dialog.dialog_saveFile(self.lastdir,  parent=self)
        filenameInfo = QFileInfo(filename)
        path = filenameInfo.absolutePath() + "/"

        # Cancel or quit the dialog.
        if not filename:
            return filename

        # Validate the suffix
        # TODO: Show information about the modification?
        if not filenameInfo.completeSuffix() == self.BATCH["SUFFIX"]:
            fileCompleteName = filenameInfo.baseName() + "." \
                + self.BATCH["SUFFIX"]
            filename = path + fileCompleteName

        # Change interface and preset for further dialogs (lastdir)
        # TODO: Check whether use path here is possible
        self.lastdir = filenameInfo.absolutePath()
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
        if not self.files:
            enable = False
        if not any([btn.isChecked() for btn in self.window.BtnParameters.buttons()]):
            enable = False

        # TODO: use a porperty to separate the ui from the logic?
        self.window.btnCalculate.setEnabled(enable)

        return enable


    def open_indexed_file(self, index):
        """
        Retrieve the data of the selected file of the list.

        Used for applying the data after clicking on the list.

        Parameters
        ----------
        index : QModelIndex or int
            Transmitted by the list. Or manually.

        Returns
        -------
        None.

        """

        # TODO: Errorhandling?
        # Distinguish given index by numerical value (from another method) or
        # is given by the ListModel (by an click event)
        if isinstance(index, QModelIndex):
            index = index.row()

        if index >= 0:
            self.parent().apply_data(self.files[index])



    ### Interaction with the FileSet self.files.


    def update_filelist(self, filelist:list):
        """
        Updates the filelist and refreshes the ui.

        Parameters
        ----------
        filelist : list of strings
            List of strings including valid urls/filenames.

        Returns
        -------
        None.

        """
        self.files.update(filelist)


    def reset_files(self):
        """Resets the filelist."""
        self.files.clear()




##############################################################################
# HACK TEST AREA