#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 22:44:59 2020

@author: Hauke Wernecke
"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



class SpectrumHandler(FileSystemEventHandler):
    def __init__(self, onModifiedMethod):
        super().__init__()
        self.onModifiedMethod = onModifiedMethod or print

    def on_modified(self, event):
        # Only consider File events.
        if event.is_directory:
            return

        self.onModifiedMethod(event.src_path)


class Watchdog():

    def __init__(self, onModifiedMethod=None):
        self.observer = Observer()
        self.handler = SpectrumHandler(onModifiedMethod)


    def start(self, paths:str)->None:
        for path in paths:
            self.observer.schedule(self.handler, path, recursive=False)
        self.observer.start()


    def stop(self)->None:
        try:
            self.observer.unschedule_all()
            self.observer.stop()
            self.observer.join()
            print("Observation stopped.")
        except RuntimeError:
            print("No observer initialized.")

    def is_alive(self)->bool:
        return self.observer.is_alive()
