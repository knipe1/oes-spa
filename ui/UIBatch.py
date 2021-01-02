#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:00:10 2020

@author: Hauke Wernecke
"""

# TODO: get_defaults?

# standard libs

# third-party libs
from PyQt5.QtCore import QObject, Slot
from PyQt5.QtWidgets import QAbstractItemView

# local modules/libs
from ui.ui_batch_dialog import Ui_batch
from ui.matplotlibwidget import MatplotlibWidget

# enums and dataclasses
from c_enum.CHARACTERISTIC import CHARACTERISTIC as CHC

# constants
TRACE_SELECTION = [CHC.PEAK_AREA,
                   CHC.PEAK_HEIGHT,
                   CHC.CHARACTERISTIC_VALUE]


class UIBatch(Ui_batch, QObject):
    """
    Extends the  PyQt5-generated class.

    Methods can be added (like set_all) or connections etc can be made without
    handling the normal generated class, which is overridden whenever the gui
    is changed.
    """

    def keyPressEvent(self, event)->None:
        print("HALASDHLASDJLADJ")


    ### Properties

    @property
    def currentTraceValue(self)->str:
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


    @property
    def plotTraceSpectrum(self)->MatplotlibWidget:
        return self.mplTrace


    ## Qt-Slots

    @Slot(bool)
    def slot_enableAnalysis(self, status:bool)->None:
        self.btnAnalyze.setEnabled(status)


    @Slot(str)
    def slot_batchfile(self, filename:str)->None:
        self.foutBatchfile.setText(filename)


    @Slot(str)
    def slot_WDdirectory(self, dirname:str)->None:
        self.foutWatchdog.setText(dirname)


    @Slot(bool)
    def slot_enableWD(self, status:bool)->None:
        self.btnSetWatchdogDir.setEnabled(status)
        self.btnSetFilename.setEnabled(status)
        self.btnWatchdog.setChecked(not status)


    @Slot(float)
    def slot_progress(self, percentage:float)->None:
        self.barProgress.setValue(percentage*100)


    ### Methods
    def __init__(self, parent):
        super().__init__()
        self.setupUi(parent)
        self.traceValues = self.init_trace()

        # Disable option to edit the strings in the file list.
        self.listFiles.setEditTriggers(QAbstractItemView.NoEditTriggers)



    def init_trace(self)->dict:
        """Selects Characteristics that can be displayed in the plot."""
        trace = {}
        for item in TRACE_SELECTION:
            trace[item] = item.value

        return trace


    def get_update_plots(self)->bool:
        return self.radSpectra.isChecked()


    def get_plot_trace(self)->bool:
        return self.radTrace.isChecked()


    def get_export_batch(self)->bool:
        return self.radExport.isChecked()


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


    def connect_clear(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnClear.clicked.connect(fun)


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
        """Interface to connect fun to clicked signal of the button."""
        self.cmbTrace.currentTextChanged.connect(fun)


    def connect_set_watchdog_directory(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnSetWatchdogDir.clicked.connect(fun)


    def connect_watchdog(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnWatchdog.clicked.connect(fun)


