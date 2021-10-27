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
from PyQt5.QtWidgets import QTreeWidgetItem, QComboBox


# local modules/libs
from ui.ui_multi_batch import Ui_Form
from modules.filehandling.filereading.filereader import FileReader

import modules.universal as uni


# enums and dataclasses
from c_enum.characteristic import CHARACTERISTIC as CHC

# constants
BATCH_CHARACTERISTICS = [CHC.PEAK_AREA,
                         CHC.PEAK_HEIGHT,
                         CHC.PEAK_POSITION,
                         CHC.REF_AREA,
                         CHC.REF_HEIGHT,
                         CHC.REF_POSITION,
                         CHC.CHARACTERISTIC_VALUE,
                         CHC.CALIBRATION_SHIFT,
                         CHC.BASELINE]



class TreeTopLevelItem(QTreeWidgetItem):
    def __init__(self, filename:str, treeWidget):
        super().__init__()
        self.filename = filename
        self.setText(0, uni.reduce_path(filename))

        self.file = FileReader(filename)
        self.peakNames = self.file.data.keys()


    def addChild(self):
        child = TreeChildItem()
        super().addChild(child)

        # void QTreeWidget::setItemWidget(QTreeWidgetItem *item, int column, QWidget *widget)
        characteristics = CharacteristicComboBox(self.treeWidget())
        self.treeWidget().setItemWidget(child, 2, characteristics)
        # Add peaks here
        peakNames = PeakComboBox(self.treeWidget(), self.peakNames)
        self.treeWidget().setItemWidget(child, 1, peakNames)


class CustomComboBox(QComboBox):
    OPTIONS = tuple()

    def __init__(self, parent):
        super().__init__(parent)
        self.addItems(self.OPTIONS)


    def addItems(self, texts):
        from enum import Enum
        if all((isinstance(t, Enum) for t in texts)):
            super().addItems((t.value for t in texts))
        else:
            super().addItems(texts)


class CharacteristicComboBox(CustomComboBox):
    OPTIONS = BATCH_CHARACTERISTICS


class PeakComboBox(CustomComboBox):
    def __init__(self, parent, peakNames):
        self.OPTIONS = peakNames
        super().__init__(parent)
        # self.currentIndexChanged.connect(self.getComboValue)

    # def getComboValue(self):
    #     print(self.currentText())
    #     return self.currentText()



class TreeChildItem(QTreeWidgetItem):
    def __init__(self):
        super().__init__()
        self.setText(3, "No Offset")
        self.setText(4, "-2.54")



class UIMultiBatch(Ui_Form, QObject):


    @pyqtSlot(str)
    def set_batchfilename(self, filename:str)->None:
        self.foutBatchfile.setText(filename)


    @pyqtSlot(str)
    def insert_batchfile(self, filename:str):
        item = TreeTopLevelItem(filename, self.batchlist)
        self.batchlist.insertTopLevelItem(0, item)


    @pyqtSlot(str)
    def add_analysis(self, batchfile:str):
        idxItem = self.get_batch_filenames().index(batchfile)
        item = self.batchlist.topLevelItem(idxItem)
        print(f"{idxItem}: {item.filename}")

        # addChild(QTreeWidgetItem *child)
        # child = TreeChildItem()
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
