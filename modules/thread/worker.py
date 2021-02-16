#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 14:59:28 2021

@author: hauke
"""

# standard libs

# third-party libs
from PyQt5.QtCore import Slot, QThread

# local modules/libs

# Enums


class Worker(QThread):

    ### Slots
    @Slot(bool)
    def slot_cancel(self, cancel:bool):
        self.cancel = cancel


    ### __methods__

    def __init__(self):
        super().__init__()
        self.cancel = False


    def __del__(self)->None:
        """Waits until the threads stopped processing and the delete it."""
        self.wait()
