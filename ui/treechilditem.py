#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 11:42:03 2021

@author: hauke
"""


# third-party libs
from PyQt5.QtWidgets import QTreeWidgetItem

# enums and dataclasses
from c_enum.multi_batch_setting import MultiBatchSetting


class TreeChildItem(QTreeWidgetItem):
    # def __int__(self):
    #     super().__init__()


    def get_values(self):
        w = self.treeWidget()
        xOffset = text_to_float(w.itemWidget(self, MultiBatchSetting.COL_X_OFFSET.value).text())
        yOffset = text_to_float(w.itemWidget(self, MultiBatchSetting.COL_Y_OFFSET.value).text())

        values = {
            "peakname": w.itemWidget(self, MultiBatchSetting.COL_PEAKNAME.value).currentText(),
            "CHC": w.itemWidget(self, MultiBatchSetting.COL_CHARACTERISTIC.value).currentText(),
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
