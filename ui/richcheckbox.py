#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 14:46:02 2021

@author: hauke
"""

# standard libs

# third-party libs
from PyQt5.QtWidgets import QFrame, QCheckBox
from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout
from PyQt5.QtCore import Qt

# local modules/libs
from ui.checkablelabel import CheckableLabel
import modules.universal as uni


class RichCheckbox(QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__post_init__()


    def __post_init__(self):
        self._remove_margin()
        self._add_checkbox()
        self._add_label()


    def _remove_margin(self):
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)


    def _add_checkbox(self):
        self._checkbox = QCheckBox(self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setHeightForWidth(self._checkbox.sizePolicy().hasHeightForWidth())
        self._checkbox.setSizePolicy(sizePolicy)
        self._layout.addWidget(self._checkbox)

        self.stateChanged = self._checkbox.stateChanged


    def _add_label(self):
        self._label = CheckableLabel(self)
        self._label.clicked.connect(self._checkbox.click)
        self._label.setTextFormat(Qt.RichText)
        self._layout.addWidget(self._label)



    def setText(self, *args):
        args = uni.remove_None_from_iterable(args)
        text = uni.add_html_linebreaks(*args)
        return self._label.setText(text)


    def isChecked(self, *args, **kwargs)->bool:
        return self._checkbox.isChecked(*args, **kwargs)


    def setChecked(self, *args, **kwargs)->bool:
        return self._checkbox.setChecked(*args, **kwargs)


    def connect(self, *args, **kwargs)->bool:
        return self._checkbox.connect(*args, **kwargs)
