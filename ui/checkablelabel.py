#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 15:41:42 2021

@author: hauke
"""

# third-party libs
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal


class CheckableLabel(QLabel):
    clicked=pyqtSignal()

    def mousePressEvent(self, ev):
        self.clicked.emit()
