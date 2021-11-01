#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 16:21:59 2021

@author: hauke
"""

# third-party libs
from PyQt5.QtWidgets import QPushButton


class DeleteButton(QPushButton):

    def __init__(self, slot=None, text:str="Delete"):
        super().__init__(text=text)
        self.clicked.connect(slot)
