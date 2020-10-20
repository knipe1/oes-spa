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
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget


# local modules/libs
from ConfigLoader import ConfigLoader
from custom_types.SUFFICES import SUFFICES as SUFF

# constants
DEF_LOG_FILE = "../debug.log"
DEF_WD_DIR = "./"
IMPORT_FILTER = ["Data sets (*.spk *.csv *.asc)",
               "SpexHex File (*.spk)",
               "Exported Raw spectrum (*.csv)",
               "Full information spectrum (*.asc)",
               ]
EXPORT_FILTER = ["Batch files (*.csv)",]

# Load the configuration for import, export and filesystem properties.
config = ConfigLoader()
BATCH = config.BATCH;


def critical_invalidSpectrum(parent:QWidget=None)->None:
    """
    Displays a error message that an invalid spectrum is loaded.

    Parameters
    ----------
    parent : QWidget, optional (default None)
        Used to determine the location the dialog is placed on the screen.

    """
    title = "Error: Could not load spectrum.";
    text = "File contains no valid spectrum!";
    QMessageBox.critical(parent, title, text);


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


def dialog_spectra(directory:str=None, parent:QWidget=None)->list:
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
        Return the files selected. Empty list if dialog is cancelled.

    """
    caption = "Load spectra";
    filefilter = filefilter_from_list(IMPORT_FILTER)

    filenames, _ = QFileDialog.getOpenFileNames(parent=parent, caption=caption,
                                                directory=directory, filter=filefilter,)
    return filenames;


def information_BatchAnalysisFinished(skippedFiles:list, parent:QWidget=None)->None:
    title = "Batch Analysis finished";
    text = "Skipped Files: \n" + "\n".join(skippedFiles);
    QMessageBox.information(parent, title, text);


### Export

def information_ExportFinished(filename:str, parent:QWidget=None)->None:
    title = "Successfully exported";
    text = f"Exported to: {filename}";
    QMessageBox.information(parent, title, text);


def information_ExportAborted(parent:QWidget=None)->None:
    title = "Export failed!";
    text = "Possible issues: No data found. "\
        "Could not export raw or processed spectra.";
    QMessageBox.information(parent, title, text);


def information_ExportNoSpectrum(parent:QWidget=None)->None:
    title = "No spectrum active!";
    text = "No spectrum is active, so no spectrum can be exported!";
    QMessageBox.information(parent, title, text);



def information_NormalizationFactorUndefined(parent:QWidget=None)->None:
    title = "No Normalization Factor defined!";
    text = "In the currently selected Fitting is no normalization factor of the peak defined. "\
    "Please find an example in the example_fitting.yml. "\
    "The normalization factor maps the area-relation to a characteristic value, "\
    "which may be used to determine the concentration.";
    QMessageBox.information(parent, title, text);


def dialog_LogFileNotFound(parent:QWidget=None)->None:
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


def filefilter_from_list(filterlist:list)->str:
    filterSeparator = ";;"
    return filterSeparator.join(filterlist)


def suffices_to_string(suffices:list)->str:
    strSuffices = ["." + suffix for suffix in suffices];
    strSuffices = ", ".join(strSuffices);
    return strSuffices


def update_logfile_in_configuration(logfile:str)->None:
    # Getting the current config and change the LOG_FILE property.
    config = ConfigLoader()
    config.logFile = logfile
    config.save_config()


def dialog_saveBatchfile(directory:str, presetFilename:str=None, parent:QWidget=None)->str:
    """

    Parameters
    ----------
    directory : path as a string
        Path of the default directory.
    presetFilename : string, optional
        Override the default filename for batch analysis. The default is defined in config.
    parent : QWidget (also other windows/widgets possible)
        The window is given to place the messagebox on the screen. The default is None.

    Returns
    -------
    string
        Path of the filename.

    """

    # default properties of the dialog
    title = "Set filename of the batchfile";
    filefilter = filefilter_from_list(EXPORT_FILTER)
    presetFilename = presetFilename or BATCH["DEF_FILENAME"];

    directoryWithPreset = path.join(directory, presetFilename)

    filename, _ = QFileDialog.getSaveFileName(parent, title, directoryWithPreset, filefilter);
    return filename;


def dialog_getWatchdogDirectory(directory:str=None, parent:QWidget=None)->None:
    """

    Parameters
    ----------
    directory : path as a string
        Path of the default directory.
    parent : QWidget (also other windows/widgets possible)
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