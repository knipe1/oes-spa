#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 20:58:50 2021

@author: hauke
"""


# standard libs

# third-party libs
from PyQt5.QtCore import Signal

# local modules/libs
from modules.thread.worker import Worker

# constants


class Drawer(Worker):
    signal_filename = Signal(str)

    def run(self):
        self._obj.plot_spectrum()


    def draw(self, obj):
        self._obj = obj
        self.start()
