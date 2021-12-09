#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 22:06:55 2020

@author: hauke
"""


# standard libs
import pandas as pd
import numpy as np

# third-party libs

# local modules/libs

# enums (alphabetical order)
from c_enum.characteristic import CHARACTERISTIC as CHC

# exceptions
from exception.InvalidBatchFileError import InvalidBatchFileError


DROP_NAN_COLUMNS = (
    CHC.BASELINE.value,
    # CHC.CHARACTERISTIC_VALUE.value,
    CHC.FILENAME.value,
    # CHC.FITTING_FILE.value, # cf. backwards compatibility
    CHC.HEADER_INFO.value,
    CHC.PEAK_AREA.value,
    CHC.PEAK_HEIGHT.value,
    CHC.PEAK_NAME.value,
    CHC.PEAK_POSITION.value,
)


class BaReader():

    ### __Methods__

    def __init__(self, filename:str, characteristic:str=None):
        super().__init__()
        self.read_batch(filename, characteristic)


    ### Methods

    def read_batch(self, filename:str, characteristic:str=None)->None:
        df = self._read_file(filename)
        self.data = self._data_by_peakname(df)


    def get_data(self, peak:str, characteristic:str)->(pd.Series, pd.Series):
        raw_time = self.data[peak][CHC.HEADER_INFO.value]
        data = self.data[peak][characteristic]

        time = raw_time.reset_index(drop=True)
        # time = time.to_numpy(dtype='datetime64[s]')
        time = np.asarray([t.to_pydatetime() for t in time])
        return time.copy(), data.copy()

        diffTime = time - time.iloc[0]
        return diffTime.copy(), data.copy()


    def _read_file(self, filename:str)->pd.DataFrame:
        """Reads the file with default configuration and drops NaN-lines."""
        try:
            df = pd.read_csv(filename, skiprows=1)
        except pd.errors.EmptyDataError:
            raise InvalidBatchFileError from pd.errors.EmptyDataError

        try:
            df.dropna(subset=DROP_NAN_COLUMNS, inplace=True)
        except KeyError:
            raise InvalidBatchFileError from KeyError

        df[CHC.HEADER_INFO.value] = pd.to_datetime(df[CHC.HEADER_INFO.value], dayfirst=True)
        return df


    def _data_by_peakname(self, df:pd.DataFrame)->dict:
        data = {}
        peakNames = self._get_peak_names(df)
        for peak in peakNames:
            data[peak] = df.loc[df[CHC.PEAK_NAME.value] == peak]
        return data


    def _get_peak_names(self, df:pd.DataFrame)->set:
        try:
            peakNames = set(df[CHC.PEAK_NAME.value])
        except KeyError:
            peakNames = set()
        return peakNames
