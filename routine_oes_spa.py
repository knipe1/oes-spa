#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OES-Spectra-Analysis

Single and batch analysis of OES spectra
"""

# standard libs
import sys
import sif_reader
da = sif_reader.np_open('./sample files/SIF/H2Plasma_433nm_Bor.sif')


# third-party libs
import emulator as emu
import threading as THR
from PyQt5.QtWidgets import QApplication


# local modules/libs
from ConfigLoader import ConfigLoader
import modules.Universal as uni
from modules.AnalysisWindow import AnalysisWindow
from Logger import Logger


# set up the logger
# logger = Logger(__name__)

def main():
    """Main program """
    # True
    # False

    initialSpkLoad = True
    tryDifferentFiles = False
    exportSpectra = True
    selectBatchfile = True
    selectBatchSpectra = True
    hideBatch = False
    showBatch = False or exportSpectra or selectBatchfile or selectBatchSpectra
    activateWD = False


    # Setup GUI
    app = QApplication(sys.argv)
    window = AnalysisWindow()

    window.window.clistFitting.setCurrentRow(5)
    window.window.clistFitting.item(5).setCheckState(2)
    window.window.clistFitting.item(0).setCheckState(2)

    # automatic open and close routine
    #window.window.ddFitting.setCurrentIndex(3)
    if initialSpkLoad:
        window.apply_file("./sample files/Asterix1059 1.Spk")

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
        test = THR.Thread(target=emu.select_directory)
        test.start()
        enter = THR.Thread(target=emu.key_alt_s)
        enter.start()
        # # in case of file already exists
        # yes = THR.Thread(target=emu.key_alt_j)
        # yes.start()
        window.batch.window.btnSetFilename.click()

    if selectBatchSpectra:
        window.window.wavelength = "433.1"
        selection = THR.Thread(target=emu.key_select_file, args=[10])
        selection.start()
        # window.lastdir = window.lastdir+"/Obel276"
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