#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 14:11:09 2021

@author: Hauke Wernecke
"""


# standard libs


# third-party libs
from PyQt5.QtCore import QObject, pyqtSlot


# local modules/libs
from ui.ui_multi_batch import Ui_Form
from ui.treetoplevelitem import TreeTopLevelItem




class UIMultiBatch(Ui_Form, QObject):


    @pyqtSlot(str)
    def set_batchfilename(self, filename:str)->None:
        self.foutBatchfile.setText(filename)


    @pyqtSlot(str)
    def insert_batchfile(self, filename:str):
        item = TreeTopLevelItem(filename)
        self.batchlist.prependTopLevelItem(item)


    @pyqtSlot(str)
    def add_analysis(self, batchfile:str):
        idxItem = self.get_batch_filenames().index(batchfile)
        item = self.batchlist.topLevelItem(idxItem)
        item.addChild()



    ### Methods
    def __init__(self, parent):
        super().__init__()
        self.setupUi(parent)


    def get_batch_filenames(self):
        return self.batchlist.get_batchfiles()


    def connect_import_batchfile(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnSelectBatchfile.clicked.connect(fun)


    def connect_add_batchfile(self, fun)->None:
        """Interface to connect fun to clicked signal of the button."""
        self.btnAddBatchfile.clicked.connect(fun)


    def connect_tree_settings_changed(self, fun)->None:
        """Interface to connect fun to treeSettingsChanged signal of the TreeWidget."""
        self.batchlist.treeSettingsChanged.connect(fun)
