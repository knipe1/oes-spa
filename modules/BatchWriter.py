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
from modules.FileWriter import FileWriter
import dialog_messages as dialog
import modules.Universal as uni

# Enums

# constants


class BatchWriter(FileWriter):
    """
    Writer for batchfiles.

    Can either export a set of data, or add data to an existing batchfile.
    """

    def __init__(self, filename):
        super().__init__(filename)
        self.timestamp = datetime.now()
        self.dialect = self.csvDialect


    def __repr__(self):
        info = {}
        info["filename"] = self.filename
        info["Timestamp"] = self.timestamp
        return self.__module__ + ":\n" + str(info)


    def export(self, data, columnTitles):
        """
        Writes the header, additional information, label and data into a csv file.

        Parameters
        ----------
        data : List or tuple
            List or tuple of data.
        labels : list of strings
            Describes the column titles of the data.

        """

        exportFilename = build_exp_filename(self.filename)

        with open(exportFilename, 'w', newline='') as exportFile:
            fWriter = csv.writer(exportFile, dialect=self.dialect)
            super().write_header(fWriter, self.timestamp)
            super().write_column_titles(fWriter, columnTitles)
            fWriter.writerows(data)


    def extend_data(self, data, columnTitles):
        if self.is_valid_batchfile():
            self.append_data(data)
        else:
            self.export([data], columnTitles)


    def append_data(self, data):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f, dialect=self.dialect)
            writer.writerow(data)



    def is_valid_batchfile(self):
        isValid = False
        try:
            with open(self.filename, 'r', newline='') as f:
                fReader = csv.reader(f, dialect=self.dialect)
                for row in fReader:
                    if self.MARKER["BATCH"] in row[0]:
                        isValid = True
                        break
        except FileNotFoundError:
            isValid = False
        return isValid


def build_exp_filename(filename):
    exportFilename = uni.replace_suffix(filename)
    return exportFilename