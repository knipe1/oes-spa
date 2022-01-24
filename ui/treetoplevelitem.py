#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 10:51:57 2021

@author: hauke
"""

# standard libs

# third-party libs
from ui.treewidgetitem import TreeWidgetItem


# local modules/libs
import modules.universal as uni
from modules.filehandling.filereading.bareader import BaReader
from ui.treechilditem import TreeChildItem

# enums
from c_enum.multi_batch_setting import MultiBatchColumns

class TreeTopLevelItem(TreeWidgetItem):
    def __init__(self, filename:str):
        super().__init__()
        self.filename = filename
        self.setText(MultiBatchColumns.COL_FILENAME.value, uni.reduce_path(filename))

        # TODO: handle FileNotFoundError
        file = BaReader(filename)
        self.peakNames = file.data.keys()


    def addChild(self):
        child = TreeChildItem()
        super().addChild(child)
        child.init_widgets(peakNames=self.peakNames)


    def delete(self):
        root = self.treeWidget().invisibleRootItem()
        idx = root.indexOfChild(self)
        root.takeChild(idx)
