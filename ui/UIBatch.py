#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:00:10 2020

@author: Hauke Wernecke
"""

# TODO: get_defaults?

# standard libs

# third-party libs
from PyQt5.QtCore import QCoreApplication      # To flush event pipeline.
from PyQt5.QtWidgets import QAbstractItemView

# local modules/libs
from ui.ui_batch_dialog import Ui_batch

class UIBatch(Ui_batch):
    """used to extend the normal class, which is generated by qt designer.
    Methods can be added (like set_all) or connections etc can be made without
    handling the normal generated class, which is overridden whenever the gui
    is changed"""


    ### Properties

    # Interface for the batchfile.
    # TODO: To be evaluated.
    @property
    def batchFile(self):
        """batchFile getter"""
        return self.foutCSV.text()

    @batchFile.setter
    def batchFile(self, filename:str):
        """batchFile setter"""
        self.foutCSV.setText(filename)


    ### Methods
    def __init__(self, parent):
        self.parent = parent
        self.setupUi(self.parent)

        # Disable option to edit the strings in the file list.
        self.listFiles.setEditTriggers(QAbstractItemView.NoEditTriggers)


    # TODO: use properties here?
    def get_update_plots(self):
        return self.radSpectra.isChecked()


    def get_plot_trace(self):
        return self.radTrace.isChecked()


    def get_export_batch(self):
        return self.radExport.isChecked()


    def get_fileselection(self)->int:
        return self.listFiles.currentRow()

    def set_fileselection(self, index):
        self.listFiles.setCurrentRow(index)

    def focussed_filelist(self):
        return self.listFiles.hasFocus()


    def enable_analysis(self, enable):
        self.btnCalculate.setEnabled(enable)


    ## Connect methods

    def connect_browse_files(self, fun):
        """Interface to connect fun to clicked signal of the button."""
        self.btnBrowse.clicked.connect(fun)


    def connect_calculate(self, fun):
        """Interface to connect fun to clicked signal of the button."""
        self.btnCalculate.clicked.connect(fun)


    def connect_cancel(self, fun):
        """Interface to connect fun to clicked signal of the button."""
        self.btnCancel.clicked.connect(fun)


    def connect_change_csvfile(self, fun):
        """Interface to connect fun to clicked signal of the button."""
        self.foutCSV.textChanged.connect(fun)


    def connect_clear(self, fun):
        """Interface to connect fun to clicked signal of the button."""
        self.btnClear.clicked.connect(fun)


    def connect_import_batch(self, fun):
        """Interface to connect fun to clicked signal of the button."""
        self.btnImport.clicked.connect(fun)


    def connect_select_file(self, fun):
        """Interface to connect fun to clicked signal of the button."""
        self.listFiles.clicked.connect(fun)


    def connect_set_filename(self, fun):
        """Interface to connect fun to clicked signal of the button."""
        self.btnSetFilename.clicked.connect(fun)



    def update_progressbar(self, percentage:[int, float]):
        """
        Convert the percentage and sets the value to the progress bar.

        Parameters
        ----------
        percentage : float
            The percentage.

        Returns
        -------
        int
            The percent calculated and set.

        """

        # Flush event pipeline to enable event-based cancellation.
        QCoreApplication.processEvents()
        percent = int(percentage*100);
        self.barProgress.setValue(percent);

        return percent;


