#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 10:51:57 2021

@author: hauke
"""

# standard libs

# third-party libs
from PyQt5.QtWidgets import QTreeWidgetItem


# local modules/libs
import modules.universal as uni
from modules.filehandling.filereading.bareader import BaReader
from ui.treechilditem import TreeChildItem
from ui.lineeditoffset import LineEditOffset
from ui.customcombobox import CharacteristicComboBox, PeakComboBox

# enums
from c_enum.multi_batch_setting import MultiBatchSetting

class TreeTopLevelItem(QTreeWidgetItem):
    def __init__(self, filename:str):
        super().__init__()
        self.filename = filename
        self.setText(MultiBatchSetting.COL_FILENAME.value, uni.reduce_path(filename))

        file = BaReader(filename)
        self.peakNames = file.data.keys()


    def addChild(self):
        child = TreeChildItem()
        super().addChild(child)

        parentWidget = self.treeWidget()

        # void QTreeWidget::setItemWidget(QTreeWidgetItem *item, int column, QWidget *widget)
        # Add peaks here
        peakNames = PeakComboBox(parentWidget, self.peakNames)
        self.treeWidget().setItemWidget(child, MultiBatchSetting.COL_PEAKNAME.value, peakNames)
        # Add Characteristics
        characteristics = CharacteristicComboBox(parentWidget)
        self.treeWidget().setItemWidget(child, MultiBatchSetting.COL_CHARACTERISTIC.value, characteristics)
        # Add X-Offset
        xOffset = LineEditOffset(parentWidget)
        self.treeWidget().setItemWidget(child, MultiBatchSetting.COL_X_OFFSET.value, xOffset)
        # Add Y-Offset
        yOffset = LineEditOffset(parentWidget)
        self.treeWidget().setItemWidget(child, MultiBatchSetting.COL_Y_OFFSET.value, yOffset)


    def get_values_from_child(self, idx:int):
        print(self.child(idx).get_values())
