"""This module is for general purposes and includes various functions
"""

from PyQt5.QtWidgets import QFileDialog

# CONFIG
# allowed file suffixes (seperate by ;;)
SUFFIXES = "SpexHex File (*.spk);;Exported Raw spectrum (*.csv)";

def LoadFiles(directory):
    if type(directory) not in [str]:
        raise TypeError("directory must be a apth (string)")
    filenames, _ = QFileDialog.getOpenFileNames(
            caption = 'Load file(s)',
            directory = directory, 
            filter = SUFFIXES)
    return filenames;