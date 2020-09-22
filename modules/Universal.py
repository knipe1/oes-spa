#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module is for general purposes and includes various functions.

@author: Hauke Wernecke
"""

# standard libs
import os
import re
from datetime import datetime

# third-party libs
from PyQt5.QtCore import QFileInfo, QUrl

# local modules/libs
from ConfigLoader import ConfigLoader
import dialog_messages as dialog


# Enums
from custom_types.SUFFICES import SUFFICES as SUFF

# Load the configuration for import and batch properties.
config = ConfigLoader()
BATCH = config.BATCH
EXPORT = config.EXPORT
IMPORT = config.IMPORT
TIMESTAMP = config.TIMESTAMP


def extract_absolute_path(filename):
    absolutePath = QFileInfo(filename).absolutePath()
    return absolutePath


def get_suffix(path:str)->str:
    """
    Extracts the complete suffix of the given filename.

    Returns
    -------
    fileSuffix : str
        Complete suffix in lower case.

    """

    # Use only lower case to avoid overhead for e.g. .spk & .Spk files.
    fileSuffix = QFileInfo(path).completeSuffix().lower()

    return fileSuffix


def get_valid_local_url(url:QUrl)->str:
    """
    Checks validity of the url and returns local url if valid.

    Parameters
    ----------
    url : QUrl
        Url of the file.

    Returns
    -------
    localUrl : str
        The local url of given url if valid.
        None otherwise.

    """

    if not url.isValid():
        return

    localUrl = url.toLocalFile();
    return localUrl
    if is_valid_suffix(localUrl):
        return localUrl

    return


def is_valid_suffix(filename:str):
    suffix = get_suffix(filename)
    if SUFF.has_value(suffix):
        return True
    return False


def mark_bold_red(label):
    """Embed the given label into a Rich text format."""
    return  "<b style='color:red'>" + label + "</b>"


def convert_to_hours(timedifference):
    """
    Converts the difference of datetimes (timedelta-object) into hours.

    Parameters
    ----------
    timedifference : timedelta
        The difference between to datetimes.

    Returns
    -------
    hours : float
        The converted difference in hours.

    """

    hours = 0.0
    try:
        # 1 hour = 3600 seconds and 1 day = 24 hours
        hours += timedifference.seconds / 3600
        hours += timedifference.days * 24
    except AttributeError:
        # TODO: implement logger?
        print("Could not convert {} into hours.".format(timedifference))

    return hours


def timestamp_to_string(timestamp):
    """Converts the given timestamp to a string with a pre-defined format."""
    # strftime = STRing From TIME (with a given format)
    timestampString = datetime.strftime(timestamp, TIMESTAMP["EXPORT"])
    return timestampString

def replace_suffix(filename, suffix):
    fileSuffix = get_suffix(filename)

    if not fileSuffix == suffix:
        fileInfo = QFileInfo(filename)
        path = extract_absolute_path(filename)
        filenameWithSuffix = fileInfo.baseName() + suffix
        newFilename = os.path.join(path, filenameWithSuffix)

    return newFilename


def reduce_path(url):
    """
    Reduces the url of a path in that way, that only the filename and one additional directory is returned

    Parameters
    ----------
    url : str or list of strings
        The url/path that should be reduced.

    Returns
    -------
    yield (opt. directory/) + filename as string

    """
    # TODO: delimiter for windows? or cross platforms?
    # Not in config? Due to static property?
    delimiter = "/";

    # Converting string url to list to enabel funtion for strings and lists.
    if isinstance(url, str):
        url = [url]

    try:
        for path in url:
            index = find_second_last(path, delimiter)
            if index < 0:
                text = path
            text = path[index:]
            yield text
    except:
        print("HELP: Some unknown error occured!!!")



def find_second_last(text, pattern):
    """
    Finds the second last occurence of the pattern in text.

    Parameters
    ----------
    text : str
        The text in which the patter is searched for.
    pattern : str
        The pattern to search for.

    Raises
    ------
    TypeError
        If no strings are given.

    Returns
    -------
    index : int
        -2 if the pattern is not found once
        -1 if the pattern is only found once
        index of the second last occurence of the pattern in text

    """
    if type(text) != str:
        raise TypeError("text must be a string")
    if type(pattern) != str:
        raise TypeError("pattern must be a string")

    index = None;
    if text.rfind(pattern) < 0:
        index = -2;
    else:
        index = text.rfind(pattern, 0, text.rfind(pattern))
    return index


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
    try:
        sep = BATCH["SEPARATOR"]
        for idx, text in enumerate(texts):
            index = format(idx, BATCH["INDEX_FORMAT"])
            yield index + sep + text
    except:
        print("HELP: Some unknown error occured!!!")


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order.
    https://nedbatchelder.com/blog/200712/human_sorting.html
    """
    def tryint(s):
        try:
            return int(s)
        except ValueError:
            return s

    # r'(\d+)' matches any digit number (# indicates one or more matches)
    # splitting a list of all non-numerical and numerical pattern
    return [ tryint(c) for c in re.split(r'(\d+)', text) ]