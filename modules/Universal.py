#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module is for general purposes and includes various functions

@author: Hauke Wernecke
"""

# standard libs
import re

# third-party libs
from PyQt5.QtCore import QFileInfo

# local modules/libs
from ConfigLoader import ConfigLoader
import dialog_messages as dialog

# Load the configuration for import and batch properties.
config = ConfigLoader()
IMPORT = config.IMPORT
BATCH = config.BATCH

def is_valid_filetype(url):
        """checks if the given url is valid to load the data"""

        isValid = True;
        file = url.toLocalFile();

        if not url.isValid():
            isValid = False;

        # Validate suffix.
        completeSuffix = QFileInfo(file).completeSuffix().lower()
        if not completeSuffix in IMPORT["VALID_SUFFIX"]:
            isValid = False;

        return isValid;



# def extract_xy_data(axis, label, separated=False):
#     """extract the x and y data from a axis object and return them together or
#     separated"""

#     data = None;

#     for line in axis.get_lines():
#         if line.get_label() == label:
#             if separated:
#                 data = (line.get_xdata(), line.get_ydata())
#             else:
#                 data = line.get_xydata()
#             break
#     return data


def reduce_path(url):
    """
    Reduces the url of a path in that way, that only the filename and one additional directory is returned

    Parameters
    ----------
    url : str or list of strings
        The url/path that should be reduced.

    Raises
    ------
    TypeError
        If no string is given.

    Returns
    -------
    TYPE
        origin url if no or merely one directory is found.
        Otherwise the fundtion return the filename and one directory

    """
    # TODO: delimiter for windows? or cross platforms?
    # Not in config? Due to static property?
    delimiter = "/";

    if type(url) == str:
        index = find_second_last(url, delimiter)
        if index < 0:
            return url

        return url[index:]

    if all([type(path) == str for path in url]):
        reducedUrl = [];
        for path in url:
            index = find_second_last(path, delimiter)
            if index < 0:
                reducedUrl.append(path)
            reducedUrl.append(path[index:])
        return reducedUrl;

    raise TypeError("url(s) must be a path (string)")


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

    Raises
    ------
    TypeError
        Raises if no list is given or not all items in the list are strings.

    Returns
    -------
    list
        return a list with modified elements.

    """
    if type(texts) != list:
        raise TypeError("texts must be a list")
    if all([type(text) != str for text in texts]) and texts:
        raise TypeError("text must be a string")

    return [format(idx, BATCH["INDEX_FORMAT"]) +
            BATCH["SEPARATOR"] + text
            for idx, text in enumerate(texts)]


def tryint(s):
    """
    Tries to convert s into a int.
    Used for human sort corresponding to the natural_keys function.

    Parameters
    ----------
    s : string
        String that tried to convert into integer

    Returns
    -------
    string or int
        int expression of s or s itself.

    """
    try:
        return int(s)
    except ValueError:
        return s

def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order.
    https://nedbatchelder.com/blog/200712/human_sorting.html
    """
    # r'(\d+)' matches any digit number (# indicates one or more matches)
    # splitting a list of all non-numerical and numerical pattern
    return [ tryint(c) for c in re.split(r'(\d+)', text) ]