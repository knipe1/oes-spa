#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 15:01:48 2021

@author: hauke
"""

# standard libs
import time

# third-party libs
from PyQt5.QtCore import Signal, Slot, QThread

# local modules/libs
from modules.thread.Worker import Worker

# Enums


class Plotter(Worker):
    signal_filename = Signal(str)

    def run(self):
        for file in self._files:
            if self.cancel:
                break
            time.sleep(.75)
            self.signal_filename.emit(file)


    def plot(self, files:list):
        self._files = files
        self.start()