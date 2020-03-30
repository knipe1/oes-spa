#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 10:22:44 2020

Batch-Analysis

Batch analysis of OES spectra
"""

__author__ = "Hauke Wernecke"
__copyright__ = "Copyright 2020"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Hauke Wernecke/Peter Knittel"
__email__ = "hauke.wernecke@iaf.fraunhhofer.de, peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"

# third-party libs
from PyQt5.QtCore import QFileInfo, QStringListModel, QModelIndex
from PyQt5.QtWidgets import QDialog, QAbstractItemView
from datetime import datetime
from enum import Enum

# local modules/libs
import modules.Universal as uni
import dialog_messages as dialog
from ui.UIBatch import UIBatch
from modules.FileReader import FileReader
from modules.FileWriter import FileWriter
from modules.DataHandler import DataHandler
from modules.Universal import ExportType

class CHARACTERISTIC(Enum):
    PEAK_HEIGHT = "Peak height"
    PEAK_AREA = "Peak area"
    BASELINE = "Baseline"
    PEAK_POSITION = "Peak position"
    HEADER_INFO = "Header info"

class BATCH_CONFIG(Enum):
    CHECKBOX = "checkbox"
    VALUE = "value"
    STATUS = "status"
    LABEL = "label"
    NAME = "name"

from Logger import Logger

config = uni.load_config()
# batch properties
BATCH = config["BATCH"];
# save properties
EXPORT = config["EXPORT"];

# set up the logger
logger = Logger(__name__)
logger.critical("WTF")

class BatchAnalysis(QDialog):
    """Class for batch analysis. """

    def __init__(self, parent):
        """initialize the parent class ( == QDialog.__init__(self)"""
        super(BatchAnalysis, self).__init__(parent)
        
        logger.debug("init  batch")
        
        # properties
        self._batchFile = ""

        # general settings
        self.setAcceptDrops(True)
        self.files = []
        # TODO: check whether there will be some inconsistency if self.lastdir is set
        # TODO: or if it even useful to implement it like this.
        self.lastdir = parent.lastdir
        self.model = QStringListModel()
        # init of window has to be at last, because it connects self.model i.a.
        self.window = UIBatch(self)
        # disable option to edit the strings in the file list.
        self.window.listFiles.setEditTriggers(QAbstractItemView.NoEditTriggers)


    @property
    def batchFile(self):
        return self._batchFile
    
    @batchFile.setter
    def batchFile(self, text):
        self.window.foutCSV.setText(text)
        self._batchFile = text

    # section: Events
    def dragEnterEvent(self, event):
        """
        Drag file over window event.
        Is accepted if at least one file is dragged

        Parameters
        ----------
        event : event
            The event itself.

        Returns
        -------
        None.

        """
        urls = event.mimeData().urls();
        for url in urls:
            if url.scheme() == "file":
                event.accept()

    def dropEvent(self, event):
        """Dropping File """
        # get the urls and check if they are valid.
        # Append all valid files to the list and display them
        valid_urls = [];
        # seperate valid and invalid urls
        urls = event.mimeData().urls();
        for url in urls:
            if uni.is_valid_filetype(self, url):
                valid_urls.append(url.toLocalFile())
        # updates the filelist with the valid urls and updates the ui
        self.update_filelist(valid_urls)

    # section: Methods
    def set_filename(self):
        """
        Opens a dialog to set the filename and updates the UI.
        NO setter function. Rather determine the filename e.g. after clicking the "set filename" button

        Returns
        -------
        None.

        """
        # Retrieve the filename and the corresponding info
        filename = dialog.dialog_saveFile(self.lastdir,  parent=self)
        filenameInfo = QFileInfo(filename)

        # TODO: Errorhandling?
        # 1. filename is not a string?

        # check the filename properties to have appropiate scheme
        if filename:
            # Validate the suffix
            if not filenameInfo.completeSuffix() == BATCH["SUFFIX"]:
                # TODO: Show information about the modification?
                path = filenameInfo.absolutePath() + "/"
                fileCompleteName = filenameInfo.baseName() + "." + BATCH["SUFFIX"]
                filename = path + fileCompleteName

            # Change interface and preset for further dialogs (lastdir)
            self.lastdir = str(filenameInfo.absolutePath())
            # setting the batch filename
            self.batchFile = filename
            self.update_UI()
        return filename

    def browse_spectra(self):
        """
        Opens a dialog to browse for spectra.
        If not cancelled, spectra a loaded into the list and one is displayed

        Returns
        -------
        None.

        """
        self.update_filelist(uni.load_files(self.lastdir))




    def multi_calc(self):
        """Batch process spectra and write to CSV """

        checkboxes = self.retrieve_batch_config();

        # not used due to adding value-tag later
        # keep only checked elements
        # checkboxes = [element for element in checkboxes if element["status"]]

        data, skippedFiles = self.retrieve_data(checkboxes)



        # create and format timestamp
        timestamp = datetime.now()
        timestamp = timestamp.strftime(EXPORT["FORMAT_TIMESTAMP"])

        # assemble header
        header = ["Filename"]
        header += self.extract_values_of_dict(checkboxes, BATCH_CONFIG.LABEL)

        # export in csv file
        csvWriter = FileWriter(self, self.batchFile, timestamp)
        csvWriter.write_data(data, header, ExportType.BATCH)

        dialog.information_BatchAnalysisFinished(skippedFiles, self)

    def retrieve_data(self, dictionary):
        data = []
        skippedFiles = []

        amount = len(self.files)
        for i in range(amount):
            # Update process bar
            self.update_progressbar((i+1)/amount)

            # Read out the file
            file = self.files[i]
            
            ##### test
            try:
                self.parent().apply_data(file)
                logger.info("parent(), data applied")
            except:
                pass
            
            try:
                self.parent().apply_data(file)
                logger.info("parent, data applied")
            except:
                pass
            #####
            
            self.openFile = FileReader(file)
            data_x, data_y = self.openFile.get_values()
            time, date = self.openFile.get_head()
            if not (time and date and data_x.size and data_y.size):
                skippedFiles.append(file)
                continue
            # Get Parameters
            spec_proc = DataHandler(data_x, data_y,
                        float(self.parent().window.tinCentralWavelength.text()),
                        int(self.parent().window.ddGrating.currentText()))
            # procX, procY = spec_proc.get_processed_data()
            _, avg = spec_proc.get_baseline()
            peak_height, peak_area = spec_proc.get_peak()
            _, peak_position = spec_proc.get_peak_raw()

            # TODO: Check more exlude conditions
            # excluding file if no appropiate data given like in processed spectra
            if not peak_height:
                skippedFiles.append(file)
                continue

            # link values to dicts
            # If the list of characteristics gets larger, a loop is possible by assigning a dict (works as a reference) to the value, e.g.:
            # peak_height = {}
            # dictionary[CHARACTERISTIC.PEAK_HEIGHT.value]["value"] = peak_height
            # peak_height["numerical value"] = xy
            # TODO: is dict.get() useful here?
            dictionary[CHARACTERISTIC.PEAK_HEIGHT.value][BATCH_CONFIG.VALUE.value] = peak_height
            dictionary[CHARACTERISTIC.PEAK_AREA.value][BATCH_CONFIG.VALUE.value] = peak_area
            dictionary[CHARACTERISTIC.BASELINE.value][BATCH_CONFIG.VALUE.value] = avg
            dictionary[CHARACTERISTIC.HEADER_INFO.value][BATCH_CONFIG.VALUE.value] = date + " " + time
            dictionary[CHARACTERISTIC.PEAK_POSITION.value][BATCH_CONFIG.VALUE.value] = peak_position



            # assembling the row and appending it to the data
            row = [file]
            row += self.extract_values_of_dict(dictionary, BATCH_CONFIG.VALUE)
            data.append(row)
        return data, skippedFiles

    def retrieve_batch_config(self):
        value_placeholder = 0
        properties = {}
        # make sure this is in the correct order
        labels = [CHARACTERISTIC.PEAK_HEIGHT.value,
                  CHARACTERISTIC.PEAK_AREA.value,
                  CHARACTERISTIC.BASELINE.value,
                  CHARACTERISTIC.HEADER_INFO.value,
                  CHARACTERISTIC.PEAK_POSITION.value,]

        # retrieve checkboxes and their properties
        checkboxes = [{BATCH_CONFIG.CHECKBOX.value: cb,
                       BATCH_CONFIG.NAME.value: cb.objectName(),
                       BATCH_CONFIG.STATUS.value: cb.isChecked(),
                       BATCH_CONFIG.VALUE.value: value_placeholder
                       } for cb in self.window.BtnParameters.buttons()]

        if len(checkboxes) != len(labels):
            raise ValueError("Checkboxes and labels are not fitting! Please check configuration")

        # union labels and checkboxes
        for checkbox, label in zip(checkboxes, labels):
            checkbox.update({BATCH_CONFIG.LABEL.value: label})
            properties[checkbox[BATCH_CONFIG.LABEL.value]] = checkbox
        return properties;

    def extract_values_of_dict(self, dictionary, key):
        """
        Extract the values of the given dictionary with the specifc key
        if the dictionary contains a key, value pair with "status", True

        Parameters
        ----------
        dictionary : dict
            A dict that must contain the given key and the key "status".
        key : string
            Key to retrieve the specific value of all items of the dictionary.

        Returns
        -------
        list
            Contains all items of the specific key. Empty if "status"-key does not exist in dictionary

        """
        data = []
        # check type
        if isinstance (key, Enum):
            key = key.value
        for label, item in dictionary.items():
            if item.get("status"):
                data.append(item[key])
        return data;

    def open_indexed_file(self, index):
        """
        Retrieve the data of the selected file of the list.
        Used for applying the data after clicking on the list

        Parameters
        ----------
        index : QModelIndex or int
            Transmitted by the list. Or manually

        Returns
        -------
        None.

        """
        # Checking whether the given index is provided by the list model
        if isinstance(index, QModelIndex):
            index = index.row()
        self.parent().file_open(self.files[index])



    def update_UI(self):
        """
        Updates the UI according to the currently seleceted options.
        Set Filename, Browse, Clear, and Parameters are always available.
        Availability of Calculate depends on the former elements.

        Returns
        -------
        None.

        """
        enable = True;
        # checks wheter a name was chosen
        if not self.batchFile:
            enable = False
        # Checks whether files were selected
        if not self.files:
            enable = False
        # checks whether any parameter was selected
        if not any([btn.isChecked() for btn in self.window.BtnParameters.buttons()]):
            enable = False

        self.window.btnCalculate.setEnabled(enable)



    def display_filenames(self):
        """setting the list of files"""
        files = uni.add_index_to_text(uni.reduce_path(self.files))
        self.model.setStringList(files)
        self.update_UI()

    def update_filelist(self, filelist):
        """
        Updates the filelist of the model and refreshes the ui

        Parameters
        ----------
        filelist : list of string
            List of strings including valid urls/filenames.

        Returns
        -------
        None.

        """
        self.files = list(set().union(self.files, filelist))
        self.files.sort(key=uni.natural_keys)

        # update the files if at least one is selected
        if self.files:
            isInit = self.model.index(0).row()
            self.display_filenames();
            # selects the first one if list was empty before
            if isInit:
                self.window.listFiles.setCurrentIndex(self.model.index(0))
                self.open_indexed_file(0)

    def clear(self):
        """Reset UI """
        self.files =  []
        self.display_filenames()

    def update_progressbar(self, percentage):
        """
        Convert the percentage into a percent and sets the value to the progress bar

        Parameters
        ----------
        percentage : float
            The percentage.

        Returns
        -------
        int
            The percent calculated and set.

        """
        percent = int(percentage*100);
        self.window.barProgress.setValue(percent);
        return percent;