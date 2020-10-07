#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module is for general purposes and includes various functions.

@author: Hauke Wernecke
"""

# standard libs
import os
import re
from datetime import datetime, timedelta

# third-party libs
from PyQt5.QtCore import QFileInfo, QUrl

# local modules/libs
from ConfigLoader import ConfigLoader


# Enums
from custom_types.SUFFICES import SUFFICES as SUFF

# Load the configuration for import and batch properties.
config = ConfigLoader()
BATCH = config.BATCH

# constants
from GLOBAL_CONSTANTS import EXPORT_TIMESTAMP

# Take "." and the suffix value to create the file extension.
EXPORT_SUFFIX = "." + SUFF.CSV.value


def extract_path_and_basename(filename):
    fileInfo = QFileInfo(filename)
    absolutePath = fileInfo.absolutePath()
    baseName = fileInfo.baseName()
    return absolutePath, baseName


def get_suffix(path:str)->str:
    """Extracts the complete suffix in lower case of the given path."""
    # Use only lower case to avoid overhead for e.g. .spk & .Spk files.
    fileSuffix = QFileInfo(path).completeSuffix().lower()
    return fileSuffix


def is_valid_suffix(filename:str)->bool:
    suffix = get_suffix(filename)
    return SUFF.has_value(suffix)


def get_valid_local_url(url:QUrl)->str:
    """
    Checks whether the url is valid and has a valid suffix

    Returns
    -------
    localUrl : str
        The local url of given url if valid. None otherwise.

    """

    if not url.isValid():
        return

    localUrl = url.toLocalFile();
    if is_valid_suffix(localUrl):
        return localUrl
    return


def convert_to_hours(timedifference:timedelta):
    """
    Converts the difference of datetimes into hours.

    Parameters
    ----------
    timedifference : timedelta
        The difference between to datetime-objects.

    Returns
    -------
    hours : float
        The converted difference in hours.

    """

    hours = 0.0
    # 1 hour = 3600 seconds and 1 day = 24 hours
    hours += timedifference.seconds / 3600
    hours += timedifference.days * 24

    return hours


def timestamp_to_string(timestamp, timeformat=None):
    """Converts the given timestamp to a string with a pre-defined format."""
    # strftime = STRing From TIME (with a given format)
    timeformat = timeformat or EXPORT_TIMESTAMP
    timestampString = datetime.strftime(timestamp, timeformat)
    return timestampString


def timestamp_from_string(timestamp, timeformat=None):
    """Converts the given timestamp to a string of a (pre-)defined format."""
    # Set default if not provided.
    timeformat = timeformat or EXPORT_TIMESTAMP
    # strptime = STRing To TIME (with a given format)
    timestamp = datetime.strptime(timestamp, timeformat)
    return timestamp


def replace_suffix(filename, suffix=None):
    """Replaces the suffix of the filename. Default is defined in the configuration."""
    # Note: The suffix needs to have a dot in front of the extension.
    newSuffix = suffix or EXPORT_SUFFIX

    fileSuffix = get_suffix(filename)
    if not fileSuffix == suffix:
        path, baseName = extract_path_and_basename(filename)
        newFilename = os.path.join(path, baseName + newSuffix)

    return newFilename


def reduce_path(urls:list):
    """
    Reduces the url to the filename and the parent directory.

    Returns
    -------
    yield (relative path + parent directory + filename)

    """
    for path in urls:
        # Use "NotExistingDirectory" to achieve that the resulting filepath is relative (../dir/filename.ext)
        referencePath = os.path.abspath(os.path.join(path, "../../NotExistingDirectory"))
        relativeFilepath = os.path.relpath(path, referencePath)
        yield relativeFilepath


def add_index_to_text(texts):
    """
    Adding the index of a list item in front of the item.
    May the 44th item be "Datei", then the returning element would be "  44:Datei"

    Parameters
    ----------
    texts : list of strings

    Returns
    -------
    yield: the text with the index prior

    """
    sep = BATCH["SEPARATOR"]
    for idx, text in enumerate(texts):
        index = format(idx, BATCH["INDEX_FORMAT"])
        yield index + sep + text


def natural_keys(text):
    """
    A list.sort(key=natural_keys) sorts in human order.
    https://nedbatchelder.com/blog/200712/human_sorting.html
    """
    # r'(\d+)' matches any digit number (# indicates one or more matches)
    # splitting a list of all non-numerical and numerical pattern
    return [ int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text) ]


### String markups

def mark_bold_red(label):
    """Embed the given label into a Rich text format."""
    return  "<b style='color:red'>" + label + "</b>"