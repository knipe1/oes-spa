#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OES-Spectra-Analysis

This application can display OES spectra. Moreover, it analyzes a spectrum and
it can also analyze multiple files within a 'batch analysis'.
"""

__author__ = "Peter Knittel, Hauke Wernecke"
__copyright__ = "Copyright 2019"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Peter Knittel/ Hauke Wernecke"
__email__ = "peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"

# standard libs
import sys
import loggerconfig

# third-party libs
from PyQt5.QtWidgets import QApplication

# local modules/libs
from modules.analysiswindow import AnalysisWindow


def main():
    """Main program """

    # Setup GUI
    # sys.argv is a list containing the arguments given in the command line
    app = QApplication(sys.argv)
    loggerconfig.set_up()
    window = AnalysisWindow()

    sys.exit(app.exec_())

# Run as main if executed and not included
main()
