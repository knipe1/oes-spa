#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 22:44:59 2020

@author: hauke
"""


from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from PyQt5.QtCore import QFileInfo


class MyHandler(FileSystemEventHandler):
    def __init__(self, modifiedFile=None):
        super().__init__()
        self.modifiedFile = modifiedFile or print

    def on_modified(self, event):
        # only consider FileModifiedEvent and no DirModifiedEvent
        if isinstance(event, FileModifiedEvent):
            path = event.src_path
            info = QFileInfo(path)
            if "." not in info.baseName():
                self.modifiedFile(event.src_path)


class Watchdog():

    def start(self, path, *args):
        self.file_handler = MyHandler(*args)
        self.observer = Observer()
        self.observer.schedule(self.file_handler, path, recursive=False)
        self.observer.start()

    def stop(self):
        try:
            self.observer.stop()
        except:
            print("no observer initialized.")