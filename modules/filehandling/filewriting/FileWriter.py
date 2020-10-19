#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 11:02:13 2020

@author: Hauke Wernecke
"""

# standard libs

# third-party libs

# local modules/libs
from modules.filehandling.FileFramework import FileFramework
import modules.Universal as uni

# Enums

# constants


class FileWriter(FileFramework):

    def __init__(self, filename):
        FileFramework.__init__(self, filename)
        self.dialect = self.csvDialect


    def __repr__(self):
        info = {}
        info["filename"] = self.filename
        info["Timestamp"] = self.timestamp
        return self.__module__ + ":\n" + str(info)


    def write_header(self, fWriter, timestamp):
            strTimestamp = uni.timestamp_to_string(timestamp)
            header =  self.MARKER["HEADER"] + " " + strTimestamp
            fWriter.writerow([header])


    def write_column_titles(self, fWriter, titles):
        fWriter.writerow(titles)
