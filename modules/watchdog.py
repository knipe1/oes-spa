#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 22:44:59 2020

@author: Hauke Wernecke
"""

from os import path
import logging

# third-party libs
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from loader.configloader import ConfigLoader
import modules.universal as uni


class Watchdog(QObject):

    ## Signals
    dog_alive = pyqtSignal(bool)


    ## Slots
    @pyqtSlot(str)
    def set_directory(self, directory:str)->None:
       self._directory = directory


    @pyqtSlot(bool)
    @pyqtSlot(bool, str)
    def trigger_status(self, status:bool, filename:str=None)->None:
        if status:
            self.start(filename)
        else:
            self.stop()


    ## __methods__

    def __init__(self, onModifiedMethod=None)->None:
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self.reset_observer()
        self._directory = ""
        self.handler = SpectrumEventHandler(onModifiedMethod)


    ## methods

    def start(self, filename:str)->None:
        isValid = self._validate_settings(filename)
        if isValid:
            self.observer.schedule(self.handler, self._directory, recursive=False)
            self.observer.start()
        self.dog_alive.emit(self.is_alive())


    def stop(self)->None:
        try:
            self.observer.unschedule_all()
            self.observer.stop()
            self.observer.join()
            self.reset_observer()
            self.logger.info("Observation stopped.")
        except RuntimeError:
            self.logger.info("No observer initialized.")
        self.dog_alive.emit(self.is_alive())


    def reset_observer(self)->None:
        self.observer = Observer()


    def is_alive(self)->bool:
        return self.observer.is_alive()


    def _validate_settings(self, batchFile:str)->bool:
        isWDdir = path.isdir(self._directory) or self._logger.info("Invalid WD directory!")
        batchPath, _, _ = uni.extract_path_basename_suffix(batchFile)
        isBatchdir = path.isdir(batchPath) or self._logger.info("Invalid batch directory!")
        isValid = (isWDdir and isBatchdir)
        return isValid



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
