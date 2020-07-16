#!/usr/bin/env python3
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

@author: Hauke Wernecke
"""



# third-party libs
from PyQt5.QtWidgets import QFileDialog, QMessageBox

# local modules/libs
from ConfigLoader import ConfigLoader


# Load the configuration for import, export and filesystem properties.
config = ConfigLoader()
EXPORT = config.EXPORT;
IMPORT = config.IMPORT;
FILE = config.FILE;



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



def critical_unknownSuffix(suffixes=IMPORT["VALID_SUFFIX"], parent=None):
    """
    Displays an error message if the file cannot be opened due to a wrong suffix.
    It will also display the valid suffixes.

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


def dialog_openFiles(directory, allowedSuffixes=IMPORT["SUFFIXES"],
                     singleFile=False, parent=None):
    """
    Opens a native dialog to open one or multiple files.

    Parameters
    ----------
    directory : path as a string
        Path of the default directory.
    allowedSuffixes : List of strings
        Will be set as a filter to display only files with the matched suffixes.
        The default is configured in IMPORT["SUFFIXES"].
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


    parameter = {"parent": parent, "caption": caption, "directory": directory,
                 "filter": filter, }
    if singleFile:
        filenames, _ = QFileDialog.getOpenFileName(**parameter);
    else:
        filenames, _ = QFileDialog.getOpenFileNames(**parameter);
    return filenames;

def information_BatchAnalysisFinished(skippedFiles, parent=None):
    # TODO docstring
    title = "Batch Analysis finished";
    text = "Skipped Files: \n" + "\n".join(skippedFiles);
    QMessageBox.information(parent, title, text);

def information_ExportFinished(filename, parent=None):
    # TODO docstring
    title = "Successfully exported";
    text = f"Exported to: {filename}";
    QMessageBox.information(parent, title, text);


def information_ExportAborted(parent=None):
    # TODO docstring
    title = "Export failed!";
    text = "Export failed. Possible issues: No data found. Invalid file, "\
    "could not export raw or processed spectra.";
    QMessageBox.information(parent, title, text);


def information_NormalizationFactor(parent=None):
    # TODO docstring
    title = "No Normalization Factor defined!";
    text = "In the currently selected Fitting is no normalization factor of "\
    "the peak defined. Please find an example in the example_fitting.yml. The"\
    " normalization factor is maps the area-relation to a characteristic "\
    "value, which may be used to determine the concentration.";
    QMessageBox.information(parent, title, text);


def dialog_LogFileNotFound(parent=None):
    # TODO docstring
    defaultDirectory = "../debug.log"
    # Prompt the user.
    title = "Log file could not be found";
    text = """Please select a new default path for your config file.""";
    QMessageBox.information(parent, title, text);

    # Select a new log file.
    caption = "Please select a log.file";
    filename, _ = QFileDialog.getSaveFileUrl(parent = parent,
                                             caption = caption,
                                             directory = defaultDirectory,);

    # Get the new or a default filename.
    localFilename = filename.toLocalFile()
    filename = localFilename if localFilename else defaultDirectory

    # Getting the current config and change the LOG_FILE property.
    config = ConfigLoader()
    config.logFile = filename
    config.save_config()

    return filename


def dialog_saveFile(directory: str, presetFilename="", parent=None):
    """
    TODO: description

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

    # default properties of the dialog
    title = "Set Filename";
    filter = EXPORT["DEF_BATCH_FILTER"];
    # set the default batch name
    if not presetFilename:
        presetFilename = EXPORT["DEF_BATCH_NAME"];

    # TODO: neccessary? Useful Errorhandling? Maybe log?
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