#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OES-Spectra-Analysis

Single and batch analysis of OES spectra
"""

__author__ = "Peter Knittel"
__copyright__ = "Copyright 2019"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Peter Knittel/ Hauke Wernecke"
__email__ = "peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"

# imports
import sys

import matplotlib as mpl
from PyQt5.QtWidgets import QApplication

import modules.Universal as uni
from modules.AnalysisWindow import AnalysisWindow


# set interactive backend
mpl.use("Qt5Agg")

config = uni.load_config()
# plots
PLOT = config["PLOT"];
# filesystem
FILE = config["FILE"]

def main():
    """Main program """

    # Setup GUI
    app = QApplication(sys.argv)
    window = AnalysisWindow()

    # Show Window
    window.show()
    window.file_open("H:/OES/ASTERIX1059/Asterix1059 5.Spk")
    window.save_raw("test")
    window.save_processed("test")
    window.file_open("H:/OES/ASTERIX1059/Asterix1059 5_raw.csv")
    sys.exit(app.exec_())
    

# in Py3 you just need main() without the if statement
if __name__ == '__main__':
    main()
