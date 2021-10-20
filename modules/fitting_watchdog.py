#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 22:44:59 2020

@author: Hauke Wernecke
"""


from .watchdog import Watchdog


class FittingWatchdog(Watchdog):

    ## methods

    def start(self)->None:
        self.observer.schedule(self.handler, self._directory, recursive=False)
        self.observer.start()
        self.dog_alive.emit(self.is_alive())
