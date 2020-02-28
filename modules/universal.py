"""This module is for general purposes and includes various functions
"""
import yaml

from PyQt5.QtCore import QFileInfo

import dialog_messages as dialog

def load_config():
    # load the config
    with open("./config.yml", "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return config


config = load_config()
LOAD = config["LOAD"]
BATCH = config["BATCH"]


def load_files(directory):
    # if type(directory) not in [str]:
    #     raise TypeError("directory must be a path (string)")
    # filenames, _ = QFileDialog.getOpenFileNames(
    #         caption = 'Load file(s)',
    #         directory = directory,
    #         filter = ";;".join(LOAD["SUFFIXES"]))
    # return filenames;
    return dialog.dialog_openFiles(directory, LOAD["SUFFIXES"])

def is_valid_filetype(parent, url):
        """checks if the given url is valid to load the data"""
        isValid = True;
        file = url.toLocalFile();

        if not url.isValid():
            isValid = False;

        if not QFileInfo(file).completeSuffix().lower() in LOAD["VALID_SUFFIX"]:
            isValid = False;
            dialog.critical_unknownSuffix(LOAD["VALID_SUFFIX"], parent)

        return isValid;



def extract_xy_data(axis, label, separated=False):
    """extract the x and y data from a axis object and
   return them together or separated"""
    for line in axis.get_lines():
        if line.get_label() == label:
            if separated:
                return line.get_xdata(), line.get_ydata()
            else:
                return line.get_xydata()
            break
    return None


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
    if all([type(text) != str for text in texts]):
        raise TypeError("text must be a string")

    return [format(idx, BATCH["INDEX_FORMAT"]) +
            BATCH["SEPARATOR"] + text
            for idx, text in enumerate(texts)]