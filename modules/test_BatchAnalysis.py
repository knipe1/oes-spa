#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Still a lot of untested code.
If errors occur, extend this file to test the issue.

Created on Wed Mar 18 18:28:42 2020

Testing the class BatchAnalysis

@author: Hauke Wernecke
"""

# third-party imports
import sys
import unittest
import threading as THR

# imports
import emulator as emu

# third-party classes
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QApplication

# classes
from modules.AnalysisWindow import AnalysisWindow



class TestBatchAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Setting up the ui and the corresponding variables
        """
        # UI
        cls.app = QApplication(sys.argv)
        cls.window = AnalysisWindow()
        # # display the uis
        cls.window.show()
        cls.window.batch.show()
        # # variables
        cls.batch = cls.window.batch
        cls.form = cls.window.batch.window

    @classmethod
    def tearDownClass(cls):
        # close the window if something raises an error
        cls.batch.close()
        cls.window.close()
        # Hint: Do not use cls.app.quit() here, because it will result in some side effects for other tests...



    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_specify_batchfile(self):
        """
        Test the method specify_batchfile.

        Prototype: specify_batchfile(self):

        Returns
        -------
        None.

        """
        # paths
        path = r"./sample files/"
        path = QFileInfo(path).absoluteFilePath()
        # names
        text = "filename"
        text_csv = text + ".csv"
        text_CSV = text + ".CSV"
        text_txt = text + ".txt"
        text_spk = text + ".spk"
        # files
        defaultFilename = path + "_batch.csv"
        arbitraryFilename = path + text + ".csv"


        """test default"""
        self.routine_specify_batchfile(defaultFilename)
        """test arbitrary name without suffix"""
        self.routine_specify_batchfile(arbitraryFilename, text)
        """test arbitrary name with suffix"""
        self.routine_specify_batchfile(arbitraryFilename, text_csv)
        """test cancel"""
        esc = THR.Thread(target=emu.key_reject)
        esc.start()
        # the same filename as before, but empty for the return value
        self.assertEqual(self.batch.specify_batchfile(), r"", "Filename: Cancel")
        self.assertEqual(self.form.foutBatchfile.text(), arbitraryFilename, "Filename: Cancel but old filename")


        # """ Test falsy suffixes"""
        # """spk"""
        self.routine_specify_batchfile(arbitraryFilename, text_spk)
        # """Capital CSV"""
        self.routine_specify_batchfile(arbitraryFilename, text_CSV)
        # """txt"""
        self.routine_specify_batchfile(arbitraryFilename, text_txt)

    def test_browse_spectra(self):
        """Browse spectra"""
        """Cancel selection"""
        esc = THR.Thread(target=emu.key_reject)
        esc.start()
        amount_before = self.batch.model.stringList()
        self.batch.browse_spectra()
        amount_after = self.batch.model.stringList()
        # compare before and after, no qualitativ comparison
        self.assertEqual(amount_before, amount_after, "Browse: Cancel")

        """select two files"""
        self.routine_browse_spectra(2)

        """select 100 files"""
        self.routine_browse_spectra(10, clearAfter=False)
        # update files
        self.routine_browse_spectra(10, msg="Browse: update files", isUpdate=True)


    def routine_specify_batchfile(self, expectedFilename, text=""):
        #set the name
        if text:
            arbitrary = THR.Thread(target=emu.key_arbitrary, args=[text])
            arbitrary.start()
        # accept the name
        enter = THR.Thread(target=emu.key_accept)
        enter.start()
        # in case of file already exists
        yes = THR.Thread(target=emu.key_alt_j)
        yes.start()
        self.assertEqual(self.batch.specify_batchfile(), expectedFilename, "Filename: issue text is "+text)
        self.assertEqual(self.form.foutBatchfile.text(), expectedFilename, "Filename: issue text is "+text)

    def routine_browse_spectra(self, amount, msg="", clearAfter = True, isUpdate = False):
        # if update only, there is no clear before and the amount is halfed
        if isUpdate:
            amount = amount // 2;
        amount_before = len(self.batch.model.stringList())
        # open and selecting the files
        test = THR.Thread(target=emu.key_select_file, args=[amount])
        test.start()
        self.batch.browse_spectra()
        amount_after = len(self.batch.model.stringList())
        message = msg or "Browse: " + str(amount) + " files"
        if isUpdate:
            self.assertEqual(amount_before, amount*2, message)
            self.assertEqual(amount_after, amount*2, message)
        else:
            self.assertEqual(amount_before, 0, message)
            self.assertEqual(amount_after, amount, message)
        if clearAfter:
            self.batch.clear()

if __name__ == '__main__':
    unittest.main()