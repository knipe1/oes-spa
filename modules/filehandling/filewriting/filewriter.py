#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 11:02:13 2020

@author: Hauke Wernecke
"""

# standard libs
import csv
from datetime import datetime

# third-party libs

# local modules/libs
# FileFramework: base class
from modules.filehandling.fileframework import FileFramework
import modules.universal as uni

# Enums

# constants


class FileWriter(FileFramework):

    ## __methods__

    def __init__(self, filename:str, timestamp:datetime)->None:
        super().__init__(filename)
        self.timestamp = timestamp
        self.dialect = self.csvDialect


    def __repr__(self):
        info = {}
        info["filename"] = self.filename
        info["Timestamp"] = self.timestamp
        return super().__repr__() + ":\n" + str(info)

    ## methods


    def export(self, filename:str, data:list, columnTitles:list, extraInformation:dict=None):
        extraInformation = extraInformation or {}

        with open(filename, mode='w', newline='') as exportFile:
            fWriter = csv.writer(exportFile, dialect=self.dialect)
            self.write_header(fWriter, self.timestamp)
            self.write_information(fWriter, extraInformation)
            self.write_column_titles(fWriter, columnTitles)
            self.write_data(fWriter, data)


    def write_header(self, fWriter:csv.writer, timestamp:datetime)->None:
            strTimestamp = uni.timestamp_to_string(timestamp)
            header =  self.MARKER["HEADER"] + " " + strTimestamp
            fWriter.writerow([header])


    def write_information(self, fWriter:csv.writer, information:dict)->None:
        for key, value in information.items():
            fWriter.writerow(key + ": " + value)


    def write_column_titles(self, fWriter:csv.writer, titles:list)->None:
        fWriter.writerow(titles)


    def write_data(self, fWriter:csv.writer, data:list)->None:
        fWriter.writerows(data)
