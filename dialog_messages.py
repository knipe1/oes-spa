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
    documentation:
        https://doc.qt.io/qt-5/qfiledialog.html (20.10.2020)
        https://doc.qt.io/qt-5/qmessagebox.html (20.10.2020)

Created on Tue Feb 18 10:10:29 2020

@author: Hauke Wernecke
"""

# standard libs

# third-party libs
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget

# local modules/libs
from loader.configloader import ConfigLoader
from c_enum.suffices import SUFFICES as SUFF

# constants
IMPORT_FILTER = ["Data sets (*.spk *.csv *.asc)",
               "SpexHex File (*.spk)",
               "Exported Raw spectrum (*.csv)",
               "Full information spectrum (*.asc)",
               ]
BATCH_FILTER = ["Batch files (*.ba)",]

# Load the configuration.
config = ConfigLoader()
BATCH = config.BATCH

# Message box
## critical

def critical_invalidSpectrum(parent:QWidget=None)->None:
    """
    Displays a error message that an invalid spectrum is loaded.

    Parameters
    ----------
    parent : QWidget, optional (default None)
        Used to determine the location the dialog is placed on the screen.

    """
    title = "Error: Could not load spectrum."
    text = "File contains no valid spectrum!"
    QMessageBox.critical(parent, title, text)


def critical_unknownSuffix(suffices:list=None, parent:QWidget=None)->None:
    """
    Displays an error message that the file suffix is invalid.
    It also displays the valid suffices.

    Parameters
    ----------
    suffices : list, optional (default SUFFICES)
        Contains the valid suffixes.
    parent : QWidget, optional (default None)
        Used to determine the location the dialog is placed on the screen.

    """
    suffices = suffices or SUFF.value_set()
    strSuffices = suffices_to_string(suffices)

    title = "Error: File could not be opened";
    text = f"Valid filetypes: {strSuffices}";
    QMessageBox.critical(parent, title, text);


## information

def information_batchfileUndefined(parent:QWidget=None)->None:
    title = "Batch file undefined";
    text = "Data cannot be analyzed. Please select a batchfile."
    QMessageBox.information(parent ,title, text);


def information_batchAnalysisFinished(skippedFiles:list, parent:QWidget=None)->None:
    title = "Batch Analysis finished";
    skippedFiles.insert(0, "Skipped Files:")
    text = "\n".join(skippedFiles);
    QMessageBox.information(parent ,title, text);


def information_normalizationFactorUndefined(parent:QWidget=None)->None:
    title = "Invalid Normalization Factor defined!";
    text = "In the currently selected Fitting is no normalization factor of the peak defined. "\
    "Please find an example in the example_fitting.yml. "\
    "The normalization factor maps the area-relation to a characteristic value, "\
    "which may be used to determine the concentration.";
    QMessageBox.information(parent, title, text);


def information_normalizationOffsetUndefined(parent:QWidget=None)->None:
    title = "Invalid Normalization Offet defined!";
    text = "In the currently selected Fitting is valid normalization offset of the peak defined. "\
    "Please find an example in the example_fitting.yml. "\
    "The normalization offset shifts the characteristic value, "\
    "which may be used to determine the concentration.";
    QMessageBox.information(parent, title, text);


### Export

def information_exportFinished(filename:str, parent:QWidget=None)->None:
    title = "Successfully exported!";
    text = f"Exported to: {filename}";
    QMessageBox.information(parent, title, text);


def information_exportAborted(parent:QWidget=None)->None:
    title = "Export failed!";
    text = "Possible issues: No data found. "\
        "Could not export raw or processed spectra.";
    QMessageBox.information(parent, title, text);


def information_exportNoSpectrum(parent:QWidget=None)->None:
    title = "No spectrum active!";
    text = "No spectrum is active, so no spectrum can be exported!";
    QMessageBox.information(parent, title, text);


# Dialogs

def dialog_spectra(parent:QWidget=None)->list:
    """
    Opens a native dialog to open one or multiple spectra.

    Parameters
    ----------
    directory : str, optional (default None)
        Entry directory of the dialog.
    parent : QWidget, optional (default None)
        Used to determine the location the dialog is placed on the screen.

    Returns
    -------
    filenames: list
        Return one or more existing files selected by the user. Empty list if cancelled.

    """
    caption = "Load spectra";
    filefilter = filefilter_from_list(IMPORT_FILTER)

    filenames, _ = QFileDialog.getOpenFileNames(parent=parent, caption=caption, filter=filefilter,)
    return filenames;


def dialog_logFile(defaultFile:str, parent:QWidget=None)->str:
    """
    Native dialog to select a new log file.

    Parameters
    ----------
    parent : QWidget, optional (default None)
        Used to determine the location the dialog is placed on the screen.

    Returns
    -------
    logfilename: str
        The filename of the log.

    """
    title = "Unable to find log file.";
    text = """Please select a new default path for the log file.""";
    QMessageBox.information(parent, title, text);

    # Select a new log file.
    caption = "Please select a log file";
    url, _ = QFileDialog.getSaveFileUrl(parent=parent, caption=caption,
                                        directory=defaultFile,);

    localFilename = url.toLocalFile()
    logfilename = localFilename if localFilename else defaultFile

    update_logfile_in_configuration(logfilename)
    return logfilename


def dialog_batchfile(parent:QWidget=None)->str:
    """
    Native dialog to select the location of the batchfile.

    Parameters
    ----------
    parent : QWidget, optional (default None)
        Used to determine the location the dialog is placed on the screen.

    Returns
    -------
    filename: str
        Path of the filename.

    """
    caption = "Set the filename of the batchfile:";
    filefilter = filefilter_from_list(BATCH_FILTER)
    defaultFilename = BATCH["DEF_FILENAME"];

    filename, _ = QFileDialog.getSaveFileName(parent=parent, caption=caption,
                                              directory=defaultFilename, filter=filefilter);
    return filename;


def dialog_importBatchfile(parent:QWidget=None)->None:
    """
    Parameters
    ----------
    directory : str, optional (default None)
        Entry directory of the dialog.
    parent : QWidget, optional (default None)
        Used to determine the location the dialog is placed on the screen.
    """
    caption = "Open batchfile"
    filefilter = filefilter_from_list(BATCH_FILTER)

    filename, _ = QFileDialog.getOpenFileName(parent=parent, caption=caption, filter=filefilter,)
    return filename



def dialog_watchdogDirectory(parent:QWidget=None)->str:
    """
    Native dialog to select an existing directory.

    Parameters
    ----------
    parent : QWidget, optional (default None)
        Used to determine the location the dialog is placed on the screen.

    Returns
    -------
    selectedDir : string
        Path of the selected directory.

    """
    caption = 'Enable live tracking of ...'
    selectedDir = QFileDialog.getExistingDirectory(parent=parent, caption=caption,)
    return selectedDir


# Helper

def filefilter_from_list(filterlist:list)->str:
    filterSeparator = ";;"
    return filterSeparator.join(filterlist)


def suffices_to_string(suffices:list)->str:
    strSuffices = ["." + suffix for suffix in suffices]
    strSuffices = ", ".join(strSuffices)
    return strSuffices


def update_logfile_in_configuration(logfile:str)->None:
    # Getting the current config and change the LOG_FILE property.
    config = ConfigLoader()
    config.logFile = logfile
    config.save_config()
