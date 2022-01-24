#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 20:58:50 2021

@author: hauke
"""


# standard libs

# third-party libs

# local modules/libs
from .worker import Worker

# constants


class Drawer(Worker):

    def run(self):
        self._obj.plot_spectrum()


    def draw(self, obj):
        self._obj = obj
        self.start()
