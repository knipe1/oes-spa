# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 18:28:42 2020

Testing the class BatchAnalysis

@author: wernecke
"""

import sys
from unittest import TestCase

from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from modules.AnalysisWindow import AnalysisWindow

import emulator as emu
import threading as thrd


app = QApplication(sys.argv)
window = AnalysisWindow()


class TestBatchAnalysis(TestCase):
    def setUp(self):
        window.show()
        window.batch.show()
        self.batch = window.batch
        self.form = window.batch.mui

    def routine_set_filename(self, expectedFilename, text=""):
        """Capital CSV"""
        #set the name
        if text:
            arbitrary = thrd.Thread(target=emu.key_arbitrary(text))
            arbitrary.start()
        # accept the name
        enter = thrd.Thread(target=emu.key_accept)
        enter.start()
        # in case of file already exists
        yes = thrd.Thread(target=emu.key_alt_j)
        yes.start()
        self.assertEqual(self.batch.set_filename(), expectedFilename, "Filename: issue text is "+text)
        self.assertEqual(self.form.foutCSV.text(), expectedFilename, "Filename: issue text is "+text)

    def routine_browse_spectra(self, amount, msg="", clearAfter = True, isUpdate = False):
        if isUpdate:
            amount = amount // 2;
        amount_before = len(self.batch.model.stringList())
        test = thrd.Thread(target=emu.key_select_file, args=[amount])
        test.start()
        self.batch.browse_spectra()
        amount_after = len(self.batch.model.stringList())
        message = msg or "Brose: " + str(amount) + " files"
        if isUpdate:
            self.assertEqual(amount_before, amount*2, message)
            self.assertEqual(amount_after, amount*2, message)
        else:
            self.assertEqual(amount_before, 0, message)
            self.assertEqual(amount_after, amount, message)
        if clearAfter:
            self.batch.clear()


    def test_set_filename(self):
        """
        Test the method set_filename.

        Prototype: set_filename(self):

        Returns
        -------
        None.

        """
        text = "Dateiname"
        text_csv = "Dateiname.csv"
        text_CSV = "Dateiname.CSV"
        text_txt = "Dateiname.txt"
        text_spk = "Dateiname.spk"
        defaultFilename = r"H:/OES/ASTERIX1059/_batch.csv"
        arbitraryFilename = r"H:/OES/ASTERIX1059/"+text+".csv"


        """test default"""
        self.routine_set_filename(defaultFilename)
        """test arbitrary name without suffix"""
        self.routine_set_filename(arbitraryFilename, text)
        """test arbitrary name with suffix"""
        self.routine_set_filename(arbitraryFilename, text_csv)
        """test cancel"""
        esc = thrd.Thread(target=emu.key_reject)
        esc.start()
        # the same filename as before, but empty for the return value
        self.assertEqual(self.batch.set_filename(), r"", "Filename: Cancel")
        self.assertEqual(self.form.foutCSV.text(), arbitraryFilename, "Filename: Cancel but old filename")


        """ Test falsy suffixes"""
        """Capital CSV"""
        self.routine_set_filename(arbitraryFilename, text_CSV)
        """txt"""
        self.routine_set_filename(arbitraryFilename, text_txt)
        """spk"""
        self.routine_set_filename(arbitraryFilename, text_spk)

    def test_browse_spectra(self):
        """Browse spectra"""
        """Cancel selection"""
        esc = thrd.Thread(target=emu.key_reject)
        esc.start()
        list1 = self.batch.model.stringList()
        self.batch.browse_spectra()
        list2 = self.batch.model.stringList()
        self.assertEqual(list1, list2, "Browse: Cancel")

        """select two files"""
        self.routine_browse_spectra(2)

        """select 100 files"""
        self.routine_browse_spectra(100, clearAfter=False)
        # update files
        self.routine_browse_spectra(100, msg="Browse: update files", isUpdate=True)


