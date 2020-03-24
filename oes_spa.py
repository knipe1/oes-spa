#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OES-Spectra-Analysis

Single and batch analysis of OES spectra"""

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


from modules.AnalysisWindow import AnalysisWindow


# set interactive backend
mpl.use("Qt5Agg")


def main():
    """Main program """

    # Setup GUI
    # TODO: why sys.argv?
    # sys.argv is a list containing the arguments given in the command line
    app = QApplication(sys.argv)
    window = AnalysisWindow()

    sys.exit(app.exec_())


# Run as main if executed and not included
main()