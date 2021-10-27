#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 14:11:09 2021

@author: Hauke Wernecke
"""


# standard libs
# import functools as fct

# third-party libs
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QTreeWidgetItem
# from PyQt5.QtWidgets import QAbstractItemView

# local modules/libs
from ui.ui_multi_batch import Ui_Form

import modules.universal as uni


# enums and dataclasses
# from c_enum.characteristic import CHARACTERISTIC as CHC



class TreeTopLevelItem(QTreeWidgetItem):
    def __init__(self, filename:str):
        super().__init__()
        self.filename = filename
        self.setText(0, uni.reduce_path(filename))



class UIMultiBatch(Ui_Form, QObject):


    @pyqtSlot(str)
    def set_batchfilename(self, filename:str)->None:
        self.foutBatchfile.setText(filename)


    @pyqtSlot(str)
    def insert_batchfile(self, filename:str):
        item = TreeTopLevelItem(filename)
        self.batchlist.insertTopLevelItem(0, item)


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
