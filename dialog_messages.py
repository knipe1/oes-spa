# -*- coding: utf-8 -*-
"""
This module concentrate all messages for dialogs together.
Advantages:
    central location for adjusting messages
    maintainable and testable

Hints:
    definitions of functions:
        first, the type is given and
        second, after the underscore the name is followed in camelCase

Created on Tue Feb 18 10:10:29 2020
"""

__author__ = "Peter Knittel"
__copyright__ = "Copyright 2020"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Peter Knittel/ Hauke Wernecke"
__email__ = "peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"


from PyQt5.QtWidgets import QFileDialog, QMessageBox

import modules.Universal as uni


config = uni.load_config()
# save properties
SAVE = config["SAVE"];





def critical_unknownFiletype(parent=None):
    """
    Displays a error message due to issues while open or read the file

    Parameters
    ----------
    parent : QMainWindow (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    Returns
    -------
    None.

    """
    title = "Error: File could not be opened";
    text = "Filetype unknown or file unreadable!";
    QMessageBox.critical(parent, title, text);


def critical_unknownSuffix(suffixes, parent=None):
    """
    Displays an error message if the file cannot be opened due to a wrong suffix. It will also display the valid suffixes.

    Parameters
    ----------
    suffixes : List of strings
        Contains the valid suffixes as a list.
    parent : TQMainWindow (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    Returns
    -------
    None.

    """
    strSuffixes = ["." + suffix for suffix in suffixes];
    strSuffixes = ", ".join(strSuffixes);

    title = "Error: File could not be opened";
    text = f"Valid filetypes: {strSuffixes}";
    QMessageBox.critical(parent, title, text);


def warning_fileSelection(parent=None):
    """
    Displays a warning if a function which requires a file is executed when no file is selected.

    Parameters
    ----------
    parent : TQMainWindow (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    Returns
    -------
    None.

    """
    title = "Warning";
    text = "No File selected!";
    QMessageBox.warning(parent, title, text);


def dialog_openFiles(directory, allowedSuffixes, parent=None):
    """
    Opens a native dialog to open one or multiple files.

    Parameters
    ----------
    directory : path as a string
        Path of the default directory.
    allowedSuffixes : List of strings
        Will be set as a filter to display only files with the matched suffixes.
    parent : TQMainWindow (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    Raises
    ------
    TypeError
        If directory is not a string.

    Returns
    -------
    list of filenames
        Return the files selected. May be empty list, list with a single entry or list of entries.

    """
    caption = "Load file(s)";
    filter = ";;".join(allowedSuffixes);

    if type(directory) not in [str]:
        raise TypeError("Directory must be a path (string)");
    filenames, _ = QFileDialog.getOpenFileNames(parent = parent,
                                                caption = caption,
                                                directory = directory,
                                                filter = filter, );
    return filenames;


def dialog_saveFile(directory, presetFilename="", parent=None):
    """


    Parameters
    ----------
    directory : path as a string
        Path of the default directory.
    presetFilename : string, optional
        Override the default filename for batch analysis. The default is defined in config.
    parent : TQMainWindow (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    Raises
    ------
    TypeError
        If directory is not a string.

    Returns
    -------
    string
        Path of the filename.

    """
    title = "Set Filename";
    filter = SAVE["DEF_BATCH_FILTER"];
    # set the default batch name
    if not presetFilename:
        presetFilename = SAVE["DEF_BATCH_NAME"];


    if type(directory) not in [str]:
        raise TypeError("Directory must be a path (string)");

    # concat the path
    path = directory+"/"+presetFilename;

    # native dialog
    filename, _ = QFileDialog.getSaveFileName(parent, title, path, filter);
    return filename;


def dialog_getDirectory(directory, parent=None):
    """
    Opens a native  dialog to set the filename if not given.

    Parameters
    ----------
    directory : path as a string
        Path of the default directory.
    parent : TQMainWindow (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    Raises
    ------
    TypeError
        If directory is not a string.

    Returns
    -------
    selectedDir : string
        Path of the selected directory.

    """
    text = 'Save spectrum to...'

    if type(directory) not in [str]:
        raise TypeError("Directory must be a path (string)");

    selectedDir = QFileDialog.getExistingDirectory(parent,
                                                    caption = text,
                                                    directory = directory)
    return selectedDir