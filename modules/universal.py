"""This module is for general purposes and includes various functions
"""

from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QFileDialog, QMessageBox

# CONFIG
# allowed file suffixes (seperate by ;;)
SUFFIXES = "SpexHex File (*.spk);;Exported Raw spectrum (*.csv)";

# if used case insensitive file system, e.g. windows
# all lower case, because the suffix will be evaluated in lower case
VALID_FILE_SUFFIX = ["csv", "spk"]

def LoadFiles(directory):
    if type(directory) not in [str]:
        raise TypeError("directory must be a path (string)")
    filenames, _ = QFileDialog.getOpenFileNames(
            caption = 'Load file(s)',
            directory = directory, 
            filter = SUFFIXES)
    return filenames;

def is_valid_filetype(parent, url):
        """checks if the given url is valid to load the data"""
        isValid = True;
        file = url.toLocalFile();
        
        if not url.isValid():
            isValid = False;
        
        if not QFileInfo(file).completeSuffix().lower() in VALID_FILE_SUFFIX:
            isValid = False;
            # TODO: magic strings?
            strSuffixes = ["." + suffix for suffix in VALID_FILE_SUFFIX];
            strSuffixes = ", ".join(strSuffixes);
            QMessageBox.critical(parent, "Error: File could not be opened",
                        f"Valid filetypes: {strSuffixes}", );
        return isValid;