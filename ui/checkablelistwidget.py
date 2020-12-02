#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 08:38:37 2020

@author: hauke
"""


# standard libs

# third-party libs
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from dependencies.natsort.natsort import natsorted

# local modules/libs

class CheckableListWidget(QListWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def addItems(self, labels:list)->None:
        self.clear()
        sortedLabels = natsorted(labels)
        for label in sortedLabels:
            item = QListWidgetItem(label)
            self.addItem(item)


    def addItem(self, item:QListWidgetItem)->None:
        item = QListWidgetItem(item)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        super().addItem(item)


    def checkedItems(self)->list:
        items = []
        for index in range(self.count()):
            if self.item(index).checkState() == Qt.Checked:
                items.append(self.item(index))
        return items

    def currentText(self)->str:
        try:
            text = self.selectedItems()[0].text()
        except IndexError:
            text = ""
        return text


    def allTexts(self)->list:
        texts = []
        for i in range(self.count()):
            texts.append(self.item(i).text())
        return texts
