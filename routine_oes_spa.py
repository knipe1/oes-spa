#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OES-Spectra-Analysis

Single and batch analysis of OES spectra
"""



# standard libs
import sys

# third-party libs
from PyQt5.QtWidgets import QApplication
import threading as THR
import emulator as emu
import dialog_messages as DIA


# local modules/libs
import loggerconfig
from modules.analysiswindow import AnalysisWindow



def main():
    """Main program """
    # True
    # False

    DIA.dialog_importBatchfile()

    initialSpkLoad = True
    initialAscLoad = False
    initialSifLoad = False
    tryDifferentFiles = False
    exportSpectra = False
    showBatch = True
    selectBatchfile = False
    selectBatchSpectra = False
    hideBatch = False
    activateWD = False

    test_calibration = True
    noFiles = 50


    # Setup GUI
    app = QApplication(sys.argv)
    loggerconfig.set_up()
    window = AnalysisWindow()


    if test_calibration:
        window.window.wavelength = "388.8"
        window.window.cbCalibration.setChecked(True)


    # automatic open and close routine
    if initialSpkLoad:
        window.apply_file("./sample files/Asterix1059 1468.Spk")
        # window.apply_file('./sample files/SIF/asterix1183-h2plasma433nm-bor-sif.asc')
    if initialAscLoad:
        # window.apply_file("./sample files/acq_3832_388nm.asc") # Inverted spectrum probe
        window.apply_file("./sample files/BH-Peak-Analysis_433nm.asc")
    if initialSifLoad:
        window.apply_file('./sample files/SIF/H2Plasma_433nm_Bor.sif')


    if tryDifferentFiles:
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
        window._export_raw()
        accept_processed = THR.Thread(target=emu.key_accept)
        accept_processed.start()
        window._export_processed()
        window.apply_file("./sample files/Asterix1059 1_raw.csv")
        reject_raw = THR.Thread(target=emu.key_accept)
        reject_raw.start()
        window._export_raw()
        window.apply_file("./sample files/Asterix1059 1_processed.csv")
        reject_processed = THR.Thread(target=emu.key_accept)
        reject_processed.start()
        window._export_processed()

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
        window.batch._window.btnSetFilename.click()

    if selectBatchSpectra:
        # window.window.wavelength = "433.1"
        selection = THR.Thread(target=emu.key_select_file, args=[noFiles])
        selection.start()
        window.batch._browse_spectra()
        window.batch._window.radTrace.click()
        window.batch._window.btnAnalyze.click()

    if hideBatch:
        window.batch.hide()

    # Set WD directory
    if activateWD:
        enter = THR.Thread(target=emu.key_accept)
        enter.start()
        window.batch._window.btnSetWatchdogDir.click()

        # Activate WD
        window.batch._window.btnWatchdog.click()

    sys.exit(app.exec_())



# Run as main if executed and not included
main()
