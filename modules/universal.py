"""This module is for general purposes and includes various functions
"""
import yaml

from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QFileDialog, QMessageBox


def load_config():
    # load the config
    with open("./config.yml", "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return config


config = load_config()
LOAD = config["LOAD"]


def load_files(directory):
    if type(directory) not in [str]:
        raise TypeError("directory must be a path (string)")
    filenames, _ = QFileDialog.getOpenFileNames(
            caption = 'Load file(s)',
            directory = directory, 
            filter = ";;".join(LOAD["SUFFIXES"]))
    return filenames;

def is_valid_filetype(parent, url):
        """checks if the given url is valid to load the data"""
        isValid = True;
        file = url.toLocalFile();
        
        if not url.isValid():
            isValid = False;
        
        if not QFileInfo(file).completeSuffix().lower() in LOAD["VALID_SUFFIX"]:
            isValid = False;
            # TODO: magic strings?
            strSuffixes = ["." + suffix for suffix in LOAD["VALID_SUFFIX"]];
            strSuffixes = ", ".join(strSuffixes);
            QMessageBox.critical(parent, "Error: File could not be opened",
                        f"Valid filetypes: {strSuffixes}", );
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