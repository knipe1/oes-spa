#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 12:58:40 2020

@author: wernecke
"""

import sys
from unittest import TestCase
from PyQt5.QtTest import QTest

import PyQt5.QtCore
from PyQt5.QtWidgets import QApplication
from modules.AnalysisWindow import AnalysisWindow


app = QApplication(sys.argv)
window = AnalysisWindow()

class TestUIMain(TestCase):
    """create docstring!?!?"""
    def setUp(self):
        window.show()
        self.form = window.window