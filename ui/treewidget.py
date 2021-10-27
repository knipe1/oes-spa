#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 12:08:27 2021

@author: hauke
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QComboBox




class combocompanies(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.addItems(["Microsoft", "Apple", "Boron"])
        self.currentIndexChanged.connect(self.getComboValue)

    def getComboValue(self):
        print(self.currentText())
        return self.currentText()


class TreeWidget(QTreeWidget):
    # def __init__(self, parent):
    #     super().__init__(parent)

    def insertTopLevelItem(self, index, item):
        print("Insert Top Level Item")
        super().insertTopLevelItem(index, item)
        # combo = combocompanies(self)
        # self.setItemWidget(item, 1, combo)
        # combo = combocompanies(self)
        # self.setItemWidget(item, 0, combo)


    def get_batchfiles(self):
        root = self.invisibleRootItem()
        toplevelItemCount = root.childCount()
        return [root.child(i).filename for i in range(toplevelItemCount)]
