#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module is for general purposes and includes various functions.

@author: Hauke Wernecke
"""

# standard libs
import os
import numpy as np
from enum import Enum
from datetime import datetime, timedelta
from collections import Iterable

# third-party libs
from PyQt5.QtCore import QFileInfo, QUrl, QDir

# local modules/libs

# Enums
from c_enum.suffices import SUFFICES as SUFF

# constants
EXPORT_TIMESTAMP = '%d.%m.%Y %H:%M:%S'
EXPORT_SUFFIX = SUFF.CSV
HTML_LINEBREAK = "<br>"

#%% Suffix

def format_suffix(suffix:(str, Enum))->str:
    """Formats the Enum.value/string suffix as '.suffix'."""
    if isinstance(suffix, Enum):
        suffix = suffix.value
    if not suffix.startswith("."):
        suffix = "." + suffix
    return suffix


def is_valid_suffix(filename:str)->bool:
    """Valid suffices are defined in 'SUFFICES'."""
    _, _, suffix = extract_path_basename_suffix(filename)
    return SUFF.has_value(suffix)


def replace_suffix(filename:str, suffix:str)->str:
    """Replaces the suffix of the filename."""
    newSuffix = format_suffix(suffix)
    path, baseName, _ = extract_path_basename_suffix(filename)
    newFilename = os.path.join(path, baseName + newSuffix)
    return newFilename


#%% urls/filename

def extract_path_basename_suffix(filename:str)->(str, str, str):
    fileInfo = QFileInfo(filename)
    absolutePath = QDir.toNativeSeparators(fileInfo.absolutePath())
    baseName = fileInfo.baseName()
    suffix = fileInfo.completeSuffix().lower()
    return absolutePath, baseName, suffix


def get_valid_local_url(url:QUrl)->str:
    """
    Checks whether the url is valid and has a valid suffix.

    Returns
    -------
    localUrl : str
        The local url of given url if valid. None otherwise.

    """
    isValid = url.isValid()
    localUrl = url.toLocalFile()
    isValidSuffix = is_valid_suffix(localUrl)
    if isValid and isValidSuffix:
        return localUrl
    return None


def reduce_paths(urls:list)->str:
    """Yields the reduced url (relative dir+file)."""
    for path in urls:
        yield reduce_path(path)


def reduce_path(path:str)->str:
    """
    Reduces the url to the filename and the directory.

    Returns
    -------
        (directory + filename)

    """
    info = QFileInfo(path)
    dirname = info.absoluteDir().dirName()
    filename = info.fileName()
    filepath = dirname + os.sep + filename
    return filepath



#%% time


def timestamp_to_string(timestamp:datetime, timeformat:str=None)->str:
    """Converts the timestamp to a string with a pre-defined format."""
    # strftime = STRing From TIME (with a given format)
    timeformat = timeformat or EXPORT_TIMESTAMP
    timeString = datetime.strftime(timestamp, timeformat)
    return timeString


def timestamp_from_string(timeString:str, timeformat:str=None)->datetime:
    """Converts the string to a timestamp. String has to be formatted acc. to 'timeformat'."""
    # strptime = STRing To TIME (with a given format)
    timeformat = timeformat or EXPORT_TIMESTAMP
    timestamp = datetime.strptime(timeString, timeformat)
    return timestamp


def timedelta_to_hours(timedifference:timedelta)->float:
    """Converts the timedelta into hours."""
    # 1 hour = 3600 seconds and 1 day = 24 hours
    hours = 0.0
    hours += timedifference.seconds / 3600
    hours += timedifference.days * 24
    return hours


def convert_to_hours(timedifferences:timedelta)->float:
    """Converts the timedelta into hours."""
    if not isinstance(timedifferences, Iterable):
        timedifferences = (timedifferences, )
    timedifferences = (t.item() for t in timedifferences)
    return np.fromiter(map(timedelta_to_hours, timedifferences), dtype=float)


#%% Miscellaneous


def convert_to_float_or_time(data:np.ndarray):
    try:
        convertedData = np.array(data, dtype=float)
    except (ValueError, TypeError):
        convertedData = convert_to_time(data)
    return convertedData


def convert_to_time(data:np.ndarray)->np.ndarray:
    """Converts a iterable of strings or datetime objects to an array of datetime objects."""
    if not all((isinstance(d, datetime) for d in data)):
        data = np.asarray(tuple(map(timestamp_from_string, data)), dtype=object)
    return data


def data_are_pixel(data:np.ndarray)->bool:
    """Checks whether the dataset is comprised of pixels."""
    try:
        arePixel = (data[1] - data[0] == 1)
    except IndexError:
        arePixel = False
    return arePixel


def get_center(data:np.ndarray)->float:
    """Gets the center data point."""
    centerIdx = np.ceil(len(data) / 2 - 1)  # offset of python lists.
    center = data[int(centerIdx)]
    return center


def mark_bold_red(label:str)->str:
    """Embed the given label into a Rich text format."""
    return  f"<b style='color:red'>{label}</b>"


def add_html_linebreaks(*lines)->str:
    return  HTML_LINEBREAK.join(lines)


def remove_None_from_iterable(*iterable):
    return tuple((e for e in iterable if e is not None))
