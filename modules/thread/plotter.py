#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 15:01:48 2021

@author: hauke
"""

# standard libs
import time

# third-party libs
from PyQt5.QtCore import Signal

# local modules/libs
from modules.thread.worker import Worker

# constants
PAUSE = 0.75


class Plotter(Worker):
    fileTriggered = Signal(str)

    def run(self):
        for file in self._files:
            if self.cancel:
                break
            time.sleep(PAUSE)
            self.fileTriggered.emit(file)


    def plot(self, files:list):
        self._files = files
        self.start()
