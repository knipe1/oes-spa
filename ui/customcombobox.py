#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 10:58:46 2021

@author: hauke


Comboboxes with options declared at instanciation.

Usage: See derived classes CharacteristicComboBox and PeakComboBox.
"""

# standard libs
from enum import Enum

# third-party libs
from PyQt5.QtWidgets import QComboBox, QTreeWidget


# enums and dataclasses
from c_enum.characteristic import CHARACTERISTIC as CHC

# constants
BATCH_CHARACTERISTICS = [
    CHC.PEAK_AREA,
    CHC.PEAK_HEIGHT,
    CHC.PEAK_POSITION,
    CHC.REF_AREA,
    CHC.REF_HEIGHT,
    CHC.REF_POSITION,
    CHC.CHARACTERISTIC_VALUE,
    CHC.CALIBRATION_SHIFT,
    CHC.BASELINE
]


class CustomComboBox(QComboBox):
    OPTIONS = tuple()

    def __init__(self, parent):
        super().__init__(parent)
        self.addItems(self.OPTIONS)
        if isinstance(parent, QTreeWidget):
            self.currentIndexChanged.connect(parent.itemSelectionChanged)


    def addItems(self, texts):
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
