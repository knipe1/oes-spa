#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 22:44:59 2020

@author: hauke
"""


import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, DirModifiedEvent, FileCreatedEvent
from PyQt5.QtCore import QFileInfo


class MyHandler(FileSystemEventHandler):
    def __init__(self, modifiedFile=None):
        super().__init__()
        # self.modifiedFile = print
        self.modifiedFile = modifiedFile or print

    def on_modified(self, event):
    # def on_any_event(self, event):
        # only consider FileModifiedEvent and no DirModifiedEvent
        if isinstance(event, FileModifiedEvent):
            path = event.src_path
            # print(f'Modified Datei: {event.src_path}')
            # Avoid hidden files passed somewhere.
            info = QFileInfo(path)
            if "." not in info.baseName():
                time.sleep(0.001)
                self.modifiedFile(event.src_path)
                # self.modifiedFile(event)
        # if isinstance(event, DirModifiedEvent):
        #     print(f'Modified Dir: {event.src_path} as event: {event}')
            # self.modifiedDir(event)
    # def on_any_event(self, event):
    #     print(f'Created File: {event.src_path} as event: {event}')
    #     if isinstance(event, FileCreatedEvent):
    #         print(f'Created File: {event.src_path}')
    #         self.modifiedDir(event.src_path)


class Watchdog():

    def start(self, path, *args):
        self.file_handler = MyHandler(*args)
        self.observer = Observer()
        self.observer.schedule(self.file_handler, path, recursive=False)
        self.observer.start()
        # self.observer.join()

    def stop(self):
        try:
            self.observer.stop()
        except:
            print("no observer initialized.")


# if __name__ == "__main__":
#     path = './modules'
#     file_handler = MyHandler()
#     observer = Observer()
#     observer.schedule(file_handler, path, recursive=False)
#     observer.start()
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()