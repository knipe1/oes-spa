#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:00:10 2020

@author: Hauke Wernecke
"""

# standard libs
import functools as fct

# third-party libs
from PyQt5.QtCore import QObject, Slot
from PyQt5.QtWidgets import QAbstractItemView

# local modules/libs
from .ui_batch_dialog import Ui_batch
from .matplotlibwidget import MatplotlibWidget


class UIBatch(Ui_batch, QObject):
    """
    Extends the  PyQt5-generated class.

    Methods can be added (like set_all) or connections etc can be made without
    handling the normal generated class, which is overridden whenever the gui
    is changed.
    """

    ### Properties

    @property
    def traceSelection(self)->str:
        """Gets the current selection of cmbTrace"""
        return self.cmbTrace.currentText()


    @property
    def plotTraceSpectrum(self)->MatplotlibWidget:
        return self.mplTrace


    ## Qt-Slots

    @Slot(bool)
    def enable_analysis(self, status:bool)->None:
        self.btnAnalyze.setEnabled(status)


    @Slot(str)
    def set_batchfilename(self, filename:str)->None:
        self.foutBatchfile.setText(filename)


    @Slot(str)
    def set_WDdirectory(self, dirname:str)->None:
        self.foutWatchdog.setText(dirname)


    @Slot(bool)
    def enable_WD(self, status:bool)->None:
        self.btnSetWatchdogDir.setEnabled(not status)
        self.btnSetFilename.setEnabled(not status)
        self.btnWatchdog.setChecked(status)


    @Slot(float)
    def set_progress_bar(self, percentage:float)->None:
        self.barProgress.setValue(percentage*100)


    # ### Methods
    def __init__(self, parent):
        super().__init__()
        self.setupUi(parent)

        from modules.multibatchform import MultiBatchForm
        widget = MultiBatchForm(self.tab_multi_batch)
        # MultiBatchForm(self.frame)
        # widget.setupUi()
        # self.tabs.addTab(widget.widget, "Test")


    def get_update_plots(self)->bool:
        return self.radSpectra.isChecked()


    def get_plot_trace(self)->bool:
        return self.radTrace.isChecked()


    def get_fileselection(self)->int:
        return self.listFiles.currentRow()


    def set_fileselection(self, index:int)->None:
        self.listFiles.setCurrentRow(index)


    def is_focussed_filelist(self)->bool:
        return self.listFiles.hasFocus()


    ## Connect methods

    def connect_browse_spectra(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnBrowse.clicked.connect(fun)


    def connect_analyze(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnAnalyze.clicked.connect(fun)


    def connect_cancel(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnCancel.clicked.connect(fun)


    def connect_change_batchfile(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.foutBatchfile.textChanged.connect(fun)


    def connect_reset(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnReset.clicked.connect(fun)


    def connect_import_batchfile(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnImport.clicked.connect(fun)


    def connect_select_file(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.listFiles.currentRowChanged.connect(fun)


    def connect_set_batchfile(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnSetFilename.clicked.connect(fun)


    def connect_change_trace(self, fun)->None:
        """Interface to connect fun to text changed signal of the combobox."""
        self.cmbTrace.currentTextChanged.connect(fun)


    def connect_refresh(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnRefresh.clicked.connect(fct.partial(fun, True))


    def connect_set_watchdog_directory(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnSetWatchdogDir.clicked.connect(fun)


    def connect_watchdog(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnWatchdog.clicked.connect(fun)
