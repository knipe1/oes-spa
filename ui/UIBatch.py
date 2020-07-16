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

# enums and dataclasses
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC


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


    # TODO: dict/list?@property
    @property
    def currentTrace(self)->str:
        """Gets the current selection of cmbTrace"""
        return self.cmbTrace.currentText()


    @property
    def traceValues(self)->dict:
        """traceValues getter"""
        return self._traceValues

    @traceValues.setter
    def traceValues(self, traceValues:dict):
        """traceValues setter

        Updating the ui
        """
        self._traceValues = traceValues
        try:
            uiElement = self.cmbTrace
            uiElement.clear()
            uiElement.addItems(traceValues.values())
        except:
            pass


    ### Methods
    def __init__(self, parent):
        self.parent = parent
        self.setupUi(self.parent)
        self.traceValues = self.init_trace()

        # Disable option to edit the strings in the file list.
        self.listFiles.setEditTriggers(QAbstractItemView.NoEditTriggers)


    def init_trace(self):
        """Selects Characteristics that can be displayed in the plot."""
        # TODO: Config? Or somewhere else?
        selection = [CHC.PEAK_AREA,
                     CHC.PEAK_HEIGHT,
                     CHC.CHARACTERISTIC_VALUE]

        trace = {}
        for item in selection:
            try:
                trace[item] = item.value
            except:
                print("UIBatch: Selection contain non enum element!")

        return trace


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


    def connect_change_trace(self, fun):
        """Interface to connect fun to clicked signal of the button."""
        self.cmbTrace.currentTextChanged.connect(fun)


    # TODO: @property?
    def update_progressbar(self, percentage:[int, float]):
        """
        Convert the percentage and sets the value to the progress bar.

        Parameters
        ----------
        percentage : float
            The percentage.
        """
        # Flush event pipeline to enable event-based cancellation.
        QCoreApplication.processEvents()
        self.barProgress.setValue(percentage*100);


