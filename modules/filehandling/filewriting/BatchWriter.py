#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 10:02:18 2020

@author: Hauke Wernecke
"""

# standard libs
import csv
from datetime import datetime

# third-party libs

# local modules/libs
from modules.filehandling.filewriting.FileWriter import FileWriter

# Enums

# constants


class BatchWriter(FileWriter):
    """
    Writer for batchfiles.

    Can either export a set of data, or add data to an existing batchfile.
    """

    def __init__(self, filename):
        super().__init__(filename, name=__name__)
        self.timestamp = datetime.now()
        self.dialect = self.csvDialect


    def __repr__(self):
        info = {}
        info["filename"] = self.filename
        info["Timestamp"] = self.timestamp
        return self.__module__ + ":\n" + str(info)


    def export(self, data:list, columnTitles:list)->None:
        """
        Parameters
        ----------
        data : list
            X- and y-data.
        columnTitles : list
            Describes the column titles of the data.

        """
        super().export(self.filename, data, columnTitles)


    def extend_data(self, data:list, columnTitles:list=None)->None:
        if self.is_valid_batchfile():
            self.append_data(data)
        else:
            self.export([data], columnTitles)


    def append_data(self, data:list)->None:
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f, dialect=self.dialect)
            writer.writerow(data)


    def is_valid_batchfile(self)->None:
        isValid = False
        try:
            with open(self.filename, 'r', newline='') as f:
                fReader = csv.reader(f, dialect=self.dialect)
                for line in fReader:
                    if self.MARKER["BATCH"] in line[0]:
                        isValid = True
                        break
        except FileNotFoundError:
            pass
        return isValid

