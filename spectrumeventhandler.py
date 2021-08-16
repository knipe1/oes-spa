#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 13:57:54 2021

@author: hauke
"""

from watchdog.events import FileSystemEventHandler

from loader.configloader import ConfigLoader



class SpectrumEventHandler(FileSystemEventHandler):

    def __init__(self, onModifiedMethod)->None:
        super().__init__()
        self.onModifiedMethod = onModifiedMethod or print
        self.logfile = ConfigLoader().logFile


    def on_modified(self, event)->None:
        # Only consider File events.
        if event.is_directory:
            return
        if self.logfile in event.src_path:
            return
        self.onModifiedMethod(event.src_path)
