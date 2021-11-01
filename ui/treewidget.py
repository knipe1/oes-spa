#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 12:08:27 2021

@author: hauke
"""

# third-party libs
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtCore import pyqtSignal


class TreeWidget(QTreeWidget):

    treeSettingsChanged = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.itemSelectionChanged.connect(self.get_settings)
        header = self.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # header.setStretchLastSection(False)


    def prependTopLevelItem(self, item:QTreeWidgetItem):
        super().insertTopLevelItem(0, item)
        item.setExpanded(True)
        item.init_widgets(self)


    def get_batchfiles(self):
        root = self.invisibleRootItem()
        toplevelItemCount = root.childCount()
        return [root.child(i).filename for i in range(toplevelItemCount)]


    def get_settings(self):
        settings = {}
        root = self.invisibleRootItem()
        toplevelItemCount = root.childCount()
        for i in range(toplevelItemCount):
            topLevelChild = root.child(i)
            filename = topLevelChild.filename
            childrenCount = topLevelChild.childCount()
            settings[filename] = [topLevelChild.child(c).get_values() for c in range(childrenCount)]
        self.treeSettingsChanged.emit(settings)
        return settings
