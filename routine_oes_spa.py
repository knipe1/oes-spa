#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OES-Spectra-Analysis

Single and batch analysis of OES spectra
"""

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
from modules.Spectrum import Spectrum


# set up the logger
logger = Logger(__name__)

def main():
    """Main program """

    logger.debug("Start routine")

    # Setup GUI
    app = QApplication(sys.argv)
    window = AnalysisWindow()

    # # automatic open and close routine
    try:
        # window.export_raw()
        window.file_open("./sample files/Asterix1059 1.Spk")
        # window.export_raw()
        # window.export_processed()
        # window.file_open("./sample files/Asterix1059 1_raw.csv")
        # window.export_processed()
    except:
        pass


    # window.batch.show()
    # # text = "filename"
    # # arbitrary = thrd.Thread(target=emu.key_arbitrary, args=[text])
    # # arbitrary.start()
    # # accept the name
    # enter = thrd.Thread(target=emu.key_accept)
    # enter.start()
    # # # in case of file already exists
    # yes = thrd.Thread(target=emu.key_alt_j)
    # yes.start()
    # window.batch.window.btnSetFilename.click()
    # selection = thrd.Thread(target=emu.key_select_file, args=[10])
    # selection.start()
    # window.batch.browse_spectra()
    # window.batch.window.cbPeakHeight.click()
    # window.batch.window.cbPeakArea.click()
    # window.batch.window.cbBaseline.click()
    # window.batch.window.btnCalculate.click()
    # window.batch.hide()

    sys.exit(app.exec_())


# Run as main if executed and not included
main()