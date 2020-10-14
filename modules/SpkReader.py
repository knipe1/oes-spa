#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:11:22 2020

@author: Hauke Wernecke
"""

# standard libs
import numpy as np

# third-party libs

# local modules/libs
from modules.BaseReader import BaseReader

# Enums
from custom_types.EXPORT_TYPE import EXPORT_TYPE
from custom_types.ERROR_CODE import ERROR_CODE as ERR


class SpkReader(BaseReader):

    ### Properties

    ### __Methods__

    def __init__(self):
        # Init baseclass providing defaults and config.
        super().__init__()
        self.__post_init__()

    def __post_init__(self):
        self.set_spk_defaults()


    ### Methods

    def set_spk_defaults(self):
        # TODO: docstring
        self.dialect = self.DIALECT["name"]
        self.xColumn = self.DATA_STRUCTURE["PIXEL_COLUMN"]
        self.yColumn = self.DATA_STRUCTURE["SPK_DATA_COLUMN"]
        self.type = EXPORT_TYPE.SPECTRUM


    def readout_file(self, fReader)->dict:

        marker = self.MARKER["HEADER"]
        data = []

        for line in fReader:
            try:
                element = line[0]
            except IndexError:
                # Skip blank lines
                continue
            if is_floatable(element):
                data.append(line)
            elif marker in element:
                _, date, time = element.split()
                header = (date, time)

        data = np.array(data)

        xData = data[:, self.xColumn]
        yData = data[:, self.yColumn]
        data = np.array((xData, yData), dtype=float).transpose()

        information = {}
        information["header"] = header
        information["data"] = data
        return information


    def extract_header(self, fReader)->tuple:

        marker = self.MARKER["HEADER"]

        for line in fReader:
            try:
                cell = line[0]
            except IndexError:
                # Skip blank rows/lines.
                continue

            # date, time = self.get_header_cell(cell)
            if marker in cell:
                _, date, time = cell.split()
                return date, time
            else:
                self.logger.error(f"No valid header, marker not found '{marker}'")


    def get_header(self, element:list)->tuple:
        """
        Extracts the header of an exported (csv, and spk) file.


        Parameters
        ----------
        row: list
            Required. The row of the file containing the header information.

        Returns
        -------
        date, time: str, str
            The date and the time of the measurement of the spectrum.

        """
        _, date, time = element[0].split()
        return (date, time)


    def extract_data(self, data:list):

        keepIdx = []
        for idx, row in enumerate(data):
            keep = False
            for element in row:
                try:
                    element = float(element)
                    keep = True
                    break
                except ValueError:
                    continue
            if not keep:
                keepIdx.append(idx)
        keepIdx.reverse()
        for idx in keepIdx:
            data.pop(idx)

        data = np.array(data, dtype=float)

        xData = data[:, self.xColumn]
        yData = data[:, self.yColumn]
        data = np.array((xData, yData)).transpose()
        return data



    def preprocess(self, fReader, **kwargs):
        """
        Read out the data of a .asc-file respective to its structure.

        Parameters
        ----------
        fReader : csv.reader-object
            Reader to iterate through the csv-file.

        Returns
        -------
        data: list
            Contain the pixel/intensity values.

        """

        next(fReader)   # skip header.
        next(fReader)   # skip units.

def is_floatable(element:str)->bool:
    try:
        float(element)
        return True
    except ValueError:
        return False

