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
from modules.filehandling.filewriting.filewriter import FileWriter

# Enums

# constants


class BatchWriter(FileWriter):
    """
    Writer for batchfiles.

    Can either export a set of data, or add data to an existing batchfile.
    """

    def __init__(self, filename:str)->None:
        super().__init__(filename, timestamp=datetime.now())


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
            writer.writerows(data)


    def is_valid_batchfile(self)->None:
        isValid = False
        try:
            with open(self.filename, 'r', newline='') as f:
                fReader = csv.reader(f, dialect=self.dialect)
                for line in fReader:
                    if self.MARKER["BATCH"] in line:
                        isValid = True
                        break
        except FileNotFoundError:
            pass
        return isValid
