#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 14:11:09 2021

@author: Hauke Wernecke
"""


# standard libs
# import functools as fct
from enum import Enum

# third-party libs
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QTreeWidgetItem, QComboBox, QLineEdit


# local modules/libs
from ui.ui_multi_batch import Ui_Form
from modules.filehandling.filereading.filereader import FileReader

import modules.universal as uni


# enums and dataclasses
from c_enum.characteristic import CHARACTERISTIC as CHC

# constants
COL_FILENAME = 0
COL_PEAKNAME = 1
COL_CHARACTERISTIC = 2
COL_X_OFFSET = 3
COL_Y_OFFSET = 4

BATCH_CHARACTERISTICS = [CHC.PEAK_AREA,
                         CHC.PEAK_HEIGHT,
                         CHC.PEAK_POSITION,
                         CHC.REF_AREA,
                         CHC.REF_HEIGHT,
                         CHC.REF_POSITION,
                         CHC.CHARACTERISTIC_VALUE,
                         CHC.CALIBRATION_SHIFT,
                         CHC.BASELINE]



class LineEditOffset(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setInputMask("0000.0000")
        self.setText("0.0")


class TreeTopLevelItem(QTreeWidgetItem):
    def __init__(self, filename:str):
        super().__init__()
        self.filename = filename
        self.setText(COL_FILENAME, uni.reduce_path(filename))

        file = FileReader(filename)
        self.peakNames = file.data.keys()


    def addChild(self):
        child = TreeChildItem()
        super().addChild(child)

        # void QTreeWidget::setItemWidget(QTreeWidgetItem *item, int column, QWidget *widget)
        # Add peaks here
        peakNames = PeakComboBox(self.treeWidget(), self.peakNames, child)
        self.treeWidget().setItemWidget(child, COL_PEAKNAME, peakNames)
        # Add Characteristics
        characteristics = CharacteristicComboBox(self.treeWidget())
        self.treeWidget().setItemWidget(child, COL_CHARACTERISTIC, characteristics)
        # Add X-Offset
        xOffset = LineEditOffset()
        self.treeWidget().setItemWidget(child, COL_X_OFFSET, xOffset)
        # Add Y-Offset
        yOffset = LineEditOffset()
        self.treeWidget().setItemWidget(child, COL_Y_OFFSET, yOffset)


    def get_values_from_child(self, idx:int):
        print(self.child(idx).get_values())


class CustomComboBox(QComboBox):
    OPTIONS = tuple()

    def __init__(self, parent, item=None):
        super().__init__(parent)
        self.addItems(self.OPTIONS)
        if item:
            print("te")
            self.currentIndexChanged.connect(item.t)

    # def getComboValue(self):
    #     print(self.currentText())
    #     return self.currentText()


    def addItems(self, texts):
        if all((isinstance(t, Enum) for t in texts)):
            super().addItems((t.value for t in texts))
        else:
            super().addItems(texts)


class CharacteristicComboBox(CustomComboBox):
    OPTIONS = BATCH_CHARACTERISTICS


class PeakComboBox(CustomComboBox):
    def __init__(self, parent, peakNames, i):
        self.OPTIONS = peakNames
        super().__init__(parent, i)



class TreeChildItem(QTreeWidgetItem):
    def __int__(self):
        super().__init__()
        self.dataChanged.connect(self.t)

    def t(self):
        print("Emitted")
        self.emitDataChanged()

    def get_values(self):
        w = self.treeWidget()
        xOffset = text_to_float(w.itemWidget(self, COL_X_OFFSET).text())
        yOffset = text_to_float(w.itemWidget(self, COL_Y_OFFSET).text())


        values = {
            "peakname": w.itemWidget(self, COL_PEAKNAME).currentText(),
            "CHC": w.itemWidget(self, COL_CHARACTERISTIC).currentText(),
            "X-Offset": xOffset,
            "Y-Offset": yOffset,
        }
        return values


def text_to_float(text:str, default:float=0.0)->float:
    try:
        number = float(text)
    except ValueError:
        number = default
    return number


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
