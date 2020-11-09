#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 22:44:59 2020

@author: Hauke Wernecke
"""

from time import sleep
import csv

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

        sleep(1) # Wait for processes to run and prevent early-reading
        try:
            self.onModifiedMethod(event.src_path)
        except Exception as ex:
            with open(".wderror", 'w', newline='') as f:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                fWriter = csv.writer(f)
                fWriter.writerow([message])




class Watchdog():

    def __init__(self, onModifiedMethod=None):
        self.handler = SpectrumHandler(onModifiedMethod)


    def start(self, path):
        self.observer = Observer()
        self.observer.schedule(self.handler, path, recursive=False)
        self.observer.start()


    def stop(self):
        try:
            self.observer.stop()
            self.observer.join(1)
        except:
            print("No observer initialized.")


    def is_alive(self)->bool:
        try:
            return self.observer.is_alive()
        except AttributeError:
            return False
