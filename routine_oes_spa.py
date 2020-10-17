#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OES-Spectra-Analysis

Single and batch analysis of OES spectra
"""

# standard libs
import sys
import time

# third-party libs
import emulator as emu
import threading as THR
from PyQt5.QtWidgets import QApplication

# local modules/libs
from ConfigLoader import ConfigLoader
import modules.Universal as uni
from modules.AnalysisWindow import AnalysisWindow
from Logger import Logger
from modules.Spectrum import Spectrum


# set up the logger
# logger = Logger(__name__)

def main():
    """Main program """
    # True
    # False

    initialLoad = False
    exportSpectra = False
    showBatch = True
    selectBatchfile = True
    selectBatchSpectra = False
    hideBatch = False
    activateWD = True


    # Setup GUI
    app = QApplication(sys.argv)
    window = AnalysisWindow()

    # automatic open and close routine
    # window.export_raw()
    #window.window.ddFitting.setCurrentIndex(3)
    if initialLoad:
        window.apply_file("./sample files/SIF/388nm_Spek1_parameter only_header cut.asc")
        window.apply_file("./sample files/Asterix1059 1.Spk")
        window.apply_file("./sample files/SIF/testasc.asc")
        window.apply_file("./sample files/SIF/388nm_Spek1_reversed.asc")
        window.apply_file("./sample files/Asterix1059 1_raw.csv")
        window.apply_file("./sample files/Asterix1059 1_processed.csv")
        window.apply_file("./sample files/_batch.csv")

    if exportSpectra:
        window.apply_file("./sample files/Asterix1059 1.Spk")
        accept_raw = THR.Thread(target=emu.key_accept)
        accept_raw.start()
        window.export_raw()
        accept_processed = THR.Thread(target=emu.key_accept)
        accept_processed.start()
        window.export_processed()
        window.apply_file("./sample files/Asterix1059 1_raw.csv")
        reject_raw = THR.Thread(target=emu.key_accept)
        reject_raw.start()
        window.export_raw()
        window.apply_file("./sample files/Asterix1059 1_processed.csv")
        reject_processed = THR.Thread(target=emu.key_accept)
        reject_processed.start()
        window.export_processed()

    if showBatch:
        window.batch.show()

    # text = "filename"
    # arbitrary = THR.Thread(target=emu.key_arbitrary, args=[text])
    # arbitrary.start()
    # accept the name

    if selectBatchfile:
        # Set the Filename
        enter = THR.Thread(target=emu.key_accept)
        enter.start()
        # # in case of file already exists
        # yes = THR.Thread(target=emu.key_alt_j)
        # yes.start()
        window.batch.window.btnSetFilename.click()

    if selectBatchSpectra:
        selection = THR.Thread(target=emu.key_select_file, args=[10])
        selection.start()
        window.lastdir = window.lastdir+"/Obel276"
        window.batch.browse_spectra()
        window.batch.window.radTrace.click()
        window.batch.window.btnCalculate.click()

    if hideBatch:
        window.batch.hide()

    # Set WD directory
    if activateWD:
        enter = THR.Thread(target=emu.key_accept)
        enter.start()
        window.batch.window.btnSetWatchdogDir.click()

        # Activate WD
        window.batch.window.btnWatchdog.click()

    sys.exit(app.exec_())


# Run as main if executed and not included
main()