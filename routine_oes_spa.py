#!/usr/bin/env python3
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

# standard libs
import sys

# third-party libs
import emulator as emu
import threading as thrd
from PyQt5.QtWidgets import QApplication

# local modules/libs
import modules.Universal as uni
from modules.AnalysisWindow import AnalysisWindow
from Logger import Logger


# set up the logger
logger = Logger(__name__)
logger.info("Tüdelü")

def main():
    """Main program """
    
    logger.debug("Start routine")

    # Setup GUI
    app = QApplication(sys.argv)
    window = AnalysisWindow()

    # automatic open and close routine
    try:
        window.file_open("./sample files/Asterix1059 1.Spk")
        window.file_open("./sample files/Asterix1059 1_raw.csv")
    except:
        pass
            

    window.batch.show()
    # text = "filename"
    # arbitrary = thrd.Thread(target=emu.key_arbitrary, args=[text])
    # arbitrary.start()
    # accept the name
    enter = thrd.Thread(target=emu.key_accept)
    enter.start()
    # # in case of file already exists
    yes = thrd.Thread(target=emu.key_alt_j)
    yes.start()
    window.batch.window.btnSetFilename.click()
    selection = thrd.Thread(target=emu.key_select_file, args=[10])
    selection.start()
    window.batch.browse_spectra()
    window.batch.window.cbPeakHeight.click()
    window.batch.window.cbPeakArea.click()
    window.batch.window.cbBaseline.click()
    window.batch.window.btnCalculate.click()
    # window.batch.hide()

    sys.exit(app.exec_())


# Run as main if executed and not included
main()