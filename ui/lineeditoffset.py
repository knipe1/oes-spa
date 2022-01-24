#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 11:44:44 2021

@author: hauke
"""

# third-party libs
from PyQt5.QtWidgets import QLineEdit
from PyQt5.Qt import Qt


class LineEditOffset(QLineEdit):
    """Extends the lineedit by formatting."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setInputMask("0000.0000")
        self.setText("0.0")
        # Works both for version: '5.9.2'
        self.setAlignment(Qt.AlignRight)
        # self.setAlignment(Qt.AlignFlag.AlignRight)
        self.textChanged.connect(parent.itemSelectionChanged)
