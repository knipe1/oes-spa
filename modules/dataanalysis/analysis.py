#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 14:02:43 2021

@author: hauke
"""

import modules.universal as uni

from modules.dataanalysis.spectrumhandler import SpectrumHandler
from modules.filehandling.filereading.filereader import FileReader
from c_types.basicsetting import BasicSetting

# Enums
from c_enum.characteristic import CHARACTERISTIC as CHC


def analyze_file(setting:BasicSetting, specHandler:SpectrumHandler, file:FileReader)->tuple:
    data = []
    header = []
    results = {}
    for fitting in setting.checkedFittings:
        specHandler._process_data()
        specHandler.fit_data(fitting)
        results = merge_characteristics(specHandler, file)

        # excluding file if no appropiate data given like in processed spectra.
        if not specHandler.has_valid_peak():
            continue

        data.append(assemble_row(results))
    header = assemble_header(results)
    return data, header


def merge_characteristics(specHandler:SpectrumHandler, file:FileReader)->dict:
    results = specHandler.results
    results[CHC.FILENAME] = file.filename

    timestamp = file.timeInfo
    results[CHC.HEADER_INFO] = uni.timestamp_to_string(timestamp)
    return results


def assemble_header(data:dict)->list:
    header = [label.value for label in data.keys()]
    return header


def assemble_row(data:dict)->list:
    row = data.values()
    return row
