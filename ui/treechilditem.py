#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 11:42:03 2021

@author: hauke
"""


# third-party libs


# local modules/libs
from ui.treewidgetitem import TreeWidgetItem
from ui.lineeditoffset import LineEditOffset
from ui.customcombobox import CharacteristicComboBox, PeakComboBox


# enums and dataclasses
from c_enum.multi_batch_setting import MultiBatchColumns, MultiBatchSetting


class TreeChildItem(TreeWidgetItem):

    def init_widgets(self, peakNames:list):
        parentWidget = self.treeWidget()

        self.add_peak_selection_as_widget(parentWidget, MultiBatchColumns.COL_PEAKNAME.value, peakNames)
        self.add_characteristic_selection_as_widget(parentWidget, MultiBatchColumns.COL_CHARACTERISTIC.value)
        self.add_offset_as_widget(parentWidget, MultiBatchColumns.COL_X_OFFSET.value)
        self.add_offset_as_widget(parentWidget, MultiBatchColumns.COL_Y_OFFSET.value)
        self.add_delete_as_widget(parentWidget)


    def add_peak_selection_as_widget(self, parent, column:int, elements:list):
        cbPeaks = PeakComboBox(parent, elements)
        parent.setItemWidget(self, column, cbPeaks)


    def add_characteristic_selection_as_widget(self, parent, column:int):
        cbCharacteristics = CharacteristicComboBox(parent)
        parent.setItemWidget(self, column, cbCharacteristics)


    def add_offset_as_widget(self, parent, column:int):
        offset = LineEditOffset(parent)
        parent.setItemWidget(self, column, offset)


    def get_values(self):
        w = self.treeWidget()
        peakname = w.itemWidget(self, MultiBatchColumns.COL_PEAKNAME.value).currentText()
        characteristic = w.itemWidget(self, MultiBatchColumns.COL_CHARACTERISTIC.value).currentText()
        xOffset = text_to_float(w.itemWidget(self, MultiBatchColumns.COL_X_OFFSET.value).text())
        yOffset = text_to_float(w.itemWidget(self, MultiBatchColumns.COL_Y_OFFSET.value).text())

        values = MultiBatchSetting(
            peakname = peakname,
            characteristic = characteristic,
            xoffset = xOffset,
            yoffset = yOffset,
        )
        return values


    def delete(self):
        idx = self.parent().indexOfChild(self)
        self.parent().takeChild(idx)


def text_to_float(text:str, default:float=0.0)->float:
    try:
        number = float(text)
    except ValueError:
        number = default
    return number
