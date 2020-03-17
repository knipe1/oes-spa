# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 10:22:44 2020

@author: Wernecke
"""

"""
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

# TODO: generate docstrings

import csv
import matplotlib as mpl
from PyQt5.QtCore import Qt, QFileInfo, QStringListModel, QModelIndex
from PyQt5.QtWidgets import QDialog, QAbstractItemView

import modules.Universal as uni
import dialog_messages as dialog

# classes
from ui.UIBatch import UIBatch
from modules.FileReader import FileReader
from modules.DataHandler import DataHandler


# set interactive backend
mpl.use("Qt5Agg")

config = uni.load_config()
# batch properties
BATCH = config["BATCH"];

class BatchAnalysis(QDialog):
    """Class for batch analysis. """

    def __init__(self, parent=None):
        super(BatchAnalysis, self).__init__(parent)

        self.setAcceptDrops(True)
        self.files = []
        self.lastdir = parent.lastdir
        self.model = QStringListModel()
        # init of mui has to be at last, because it connects self.model i.a.
        self.mui = UIBatch(self)
        self.mui.listFiles.setEditTriggers(QAbstractItemView.NoEditTriggers)


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
        urls = event.mimeData().urls();
        for url in urls:
            if uni.is_valid_filetype(self, url):
                self.files.append(url.toLocalFile())
        self.display_filenames();
        self.update_UI()


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
            if not filenameInfo.suffix().lower() == BATCH["SUFFIX"]:
                # TODO: Show information about the modification?
                filename = filenameInfo.baseName + "." + BATCH["SUFFIX"]

            # Change interface and preset for further dialogs (lastdir)
            self.lastdir = str(filenameInfo.absolutePath())
            self.mui.foutCSV.setText(filename)
            self.update_UI()

    def browse_spectra(self):
        """
        Opens a dialog to browse for spectra.
        If not cancelled, spectra a loaded into the list and one is displayed

        Returns
        -------
        None.

        """
        self.files =  uni.load_files(self.lastdir);

        if self.files:
            self.display_filenames();

            self.update_UI()
            self.mui.listFiles.setCurrentIndex(self.model.index(0))
            self.open_indexed_file(0)


    def multi_calc(self):
        """Batch process spectra and write to CSV """


        # retrieve checkboxes and their properties
        checkboxes = [{"checkbox": btn,
                       "name": btn.objectName(),
                       "state": btn.isChecked()
                       } for btn in self.mui.BtnParameters.buttons()]
        # make sure this is in the correct order
        labels = ["Peak height", "Peak area", "Baseline", "Header info", "Peak position",]

        # union labels and checkboxes
        for idx, element in enumerate(checkboxes):
            element.update({"label": labels[idx]})

        # not used due to adding value-tag later
        # keep only checked elements
        # checkboxes = [element for element in checkboxes if element["state"]]


        # Set correct Filename and open it
        csvfile = str(self.mui.foutCSV.text())
        with open(csvfile, 'w', newline='') as batchFile:
             # open writer with self defined dialect
             # TODO: check/include the dialect
            csvWr = csv.writer(batchFile, )#dialect=self.dialect)

            header = ["Filename"]
            for element in checkboxes:
                if element["state"]:
                    header.append(element["label"])

            csvWr.writerow(header)

            amount = len(self.files)
            for i in range(amount):

                # Read out the file
                file = self.files[i]
                self.openFile = FileReader(file)
                data_x, data_y = self.openFile.get_values()
                time, date = self.openFile.get_head()

                # Get Parameters
                spec_proc = DataHandler(
                            data_x, data_y,
                            float(self.parent().window.tinCentralWavelength.text()),
                            int(self.parent().window.ddGrating.currentText()))
                procX, procY = spec_proc.get_processed_data()
                baseline, avg = spec_proc.get_baseline()
                peak_height, peak_area = spec_proc.get_peak()
                peak_position, peak_raw = spec_proc.get_peak_raw()



                checkboxes[0]["value"] = peak_height
                checkboxes[1]["value"] = peak_area
                checkboxes[2]["value"] = avg
                checkboxes[3]["value"] = peak_height
                checkboxes[4]["value"] = date + " " + time


                row = [file]
                for element in checkboxes:
                    if element["state"]:
                        row.append(element["value"])

                csvWr.writerow(row)

                # Update process bar
                self.update_progressbar((i+1)/amount)


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
        """sets hte percentage to the progress bar"""
        percent = int(percentage*100);
        self.mui.barProgress.setValue(percent);
        return percent;

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
        if not self.mui.foutCSV.text():
            enable = False
        # Checks whether files were selected
        if not self.files:
            enable = False
        # checks whether any parameter was selected
        if not any([btn.isChecked() for btn in self.mui.BtnParameters.buttons()]):
            enable = False

        self.mui.btnCalculate.setEnabled(enable)



    def display_filenames(self):
        """setting the list of files"""
        files = uni.add_index_to_text(uni.reduce_path(self.files))
        self.model.setStringList(files)


    def clear(self):
        """Reset UI """
        self.files =  []
        self.display_filenames()
        self.update_UI()