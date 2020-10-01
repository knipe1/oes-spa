#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module concentrate all messages for dialogs together.
Advantages:
    central location for adjusting messages

Hints:
    definitions of functions:
        first, the type is given and
        second, after the underscore the name is followed in camelCase

Created on Tue Feb 18 10:10:29 2020

@author: Hauke Wernecke
"""

# standard libs
from os import path


# third-party libs
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMainWindow


# local modules/libs
from ConfigLoader import ConfigLoader

# constants
DEF_LOG_FILE = "../debug.log"
DEF_WD_DIR = "./"

# Load the configuration for import, export and filesystem properties.
config = ConfigLoader()
EXPORT = config.EXPORT;
IMPORT = config.IMPORT;
GENERAL = config.GENERAL;



def critical_invalidSpectrum(parent:QMainWindow=None)->None:
    """
    Displays a error message that the filetype is unknown.

    Parameters
    ----------
    parent : QMainWindow (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    """
    title = "Error: File could not be opened.";
    text = "Filetype unknown or file unreadable!";
    QMessageBox.critical(parent, title, text);



def critical_unknownSuffix(suffices:list=None, parent:QMainWindow=None)->None:
    """
    Displays an error message if the file cannot be opened due to a wrong suffix.
    It will also display the valid suffixes.

    Parameters
    ----------
    suffixes : List of strings
        Contains the valid suffixes as a list.
    parent : TQMainWindow (also other windows/widgets possible)

    """

    # Set default.
    suffices = suffices or IMPORT["SUFFIX"]
    # Format the suffices.
    strSuffices = ["." + suffix for suffix in suffices];
    strSuffices = ", ".join(strSuffices);

    title = "Error: File could not be opened";
    text = f"Valid filetypes: {strSuffices}";

    QMessageBox.critical(parent, title, text);


def dialog_openBatchFile(directory:str, parent:QMainWindow=None)->None:
    caption = "Open batchfile"
    filter = EXPORT["FILTER"]

    filename, _ = QFileDialog.getOpenFileName(parent=parent,
                                              caption=caption,
                                              directory=directory,
                                              filter=filter,)
    return filename


def dialog_openSpectra(directory:str, parent:QMainWindow=None)->None:
    """
    Opens a native dialog to open one or multiple spectra.

    Parameters
    ----------
    directory : path as a string
        Path of the default directory.
    parent : TQMainWindow (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    Returns
    -------
    list of filenames
        Return the files selected. Empty list if dialog is cancelled.

    """
    caption = "Load spectra";
    filterSuffixes = IMPORT["FILTER"]
    filter = ";;".join(filterSuffixes);

    filenames, _ = QFileDialog.getOpenFileNames(parent=parent,
                                                caption=caption,
                                                directory=directory,
                                                filter=filter,)
    return filenames;


def information_BatchAnalysisFinished(skippedFiles:list, parent:QMainWindow=None)->None:
    title = "Batch Analysis finished";
    text = "Skipped Files: \n" + "\n".join(skippedFiles);
    QMessageBox.information(parent, title, text);


def information_ExportFinished(filename:str, parent:QMainWindow=None)->None:
    title = "Successfully exported";
    text = f"Exported to: {filename}";
    QMessageBox.information(parent, title, text);


def information_ExportAborted(parent:QMainWindow=None)->None:
    title = "Export failed!";
    text = "Export failed. Possible issues: No data found. Invalid file, "\
    "could not export raw or processed spectra.";
    QMessageBox.information(parent, title, text);


def information_NormalizationFactorUndefined(parent:QMainWindow=None)->None:
    title = "No Normalization Factor defined!";
    text = "In the currently selected Fitting is no normalization factor of the peak defined. "\
    "Please find an example in the example_fitting.yml. "\
    "The normalization factor maps the area-relation to a characteristic value, "\
    "which may be used to determine the concentration.";
    QMessageBox.information(parent, title, text);


def dialog_LogFileNotFound(parent:QMainWindow=None)->None:
    # Prompt the user.
    title = "Log file could not be found";
    text = """Please select a new default path for the log file.""";
    QMessageBox.information(parent, title, text);

    # Select a new log file.
    caption = "Please select a log file";
    url, _ = QFileDialog.getSaveFileUrl(parent = parent,
                                        caption = caption,
                                        directory = DEF_LOG_FILE,);

    localFilename = url.toLocalFile()
    logfile = localFilename if localFilename else DEF_LOG_FILE

    update_logfile_in_configuration(logfile)

    return logfile


def update_logfile_in_configuration(logfile:str)->None:
    # Getting the current config and change the LOG_FILE property.
    config = ConfigLoader()
    config.logFile = logfile
    config.save_config()


def dialog_saveBatchfile(directory:str, presetFilename:str=None, parent:QMainWindow=None)->None:
    """

    Parameters
    ----------
    directory : path as a string
        Path of the default directory.
    presetFilename : string, optional
        Override the default filename for batch analysis. The default is defined in config.
    parent : TQMainWindow (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    Returns
    -------
    string
        Path of the filename.

    """

    # default properties of the dialog
    title = "Set filename of the batchfile";
    filter = EXPORT["FILTER"];
    presetFilename = presetFilename or EXPORT["DEF_BATCH_NAME"];

    directoryWithPreset = path.join(directory, presetFilename)

    filename, _ = QFileDialog.getSaveFileName(parent, title, directoryWithPreset, filter);
    return filename;


def dialog_getWatchdogDirectory(directory:str=None, parent:QMainWindow=None)->None:
    """

    Parameters
    ----------
    directory : path as a string
        Path of the default directory.
    parent : TQMainWindow (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    Returns
    -------
    selectedDir : string
        Path of the selected directory.

    """
    caption = 'Enable live tracking of ...'
    directory = directory or DEF_WD_DIR

    selectedDir = QFileDialog.getExistingDirectory(parent=parent,
                                                   caption=caption,
                                                   directory=directory)
    return selectedDir