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

# TODO: return values?
from PyQt5.QtWidgets import QFileDialog, QMessageBox

def critical_unknownFiletype(parent=None):
    title = "Error: File could not be opened"
    text = "Filetype unknown or file unreadable!"
    QMessageBox.critical(parent, title, text)


def critical_unknownSuffix(suffixes, parent=None):
    strSuffixes = ["." + suffix for suffix in suffixes];
    strSuffixes = ", ".join(strSuffixes);

    title = "Error: File could not be opened"
    text = f"Valid filetypes: {strSuffixes}"
    QMessageBox.critical(parent, title, text)


def warning_fileSelection(parent=None):
    title = "Warning"
    text = "No File selected!"
    QMessageBox.warning(parent, title, text)


def dialog_openFiles(directory, allowedSuffixes, parent=None):
    caption = "Load file(s)"
    filter = ";;".join(allowedSuffixes)

    if type(directory) not in [str]:
        raise TypeError("directory must be a path (string)")
    filenames, _ = QFileDialog.getOpenFileNames(parent = parent,
                                                caption = caption,
                                                directory = directory,
                                                filter = filter)
    return filenames;


def dialog_saveFile(directory, presetFilename="batch", parent=None):
    title = "Set Filename"
    filter = "Comma separated (*.csv)"

    filename, _ = QFileDialog.getSaveFileName(parent, title, directory+"/"+presetFilename, filter)
    return filename


def dialog_getDirectory(directory, parent=None):
    # open a dialog to set the filename if not given
     text = 'Save spectrum to...'
     selectedDir = QFileDialog.getExistingDirectory(parent,
                                                    caption = text,
                                                    directory = directory)
     return selectedDir