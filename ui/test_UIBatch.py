# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 11:59:03 2020

@author: wernecke
"""

import sys
from unittest import TestCase
from PyQt5.QtTest import QTest

from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from modules.AnalysisWindow import AnalysisWindow

import emulator as emu
import threading as thrd


app = QApplication(sys.argv)
window = AnalysisWindow()


class TestUIBatch(TestCase):
    def setUp(self):
        window.show()
        window.batch.show()
        self.form = window.batch.mui


    def test_availability(self):
        """
        Test wheter elements are default enabled.

        Returns
        -------
        None.

        """
        self.assertTrue(self.form.btnSetFilename.isEnabled())
        self.assertTrue(self.form.btnBrowse.isEnabled())
        self.assertTrue(self.form.csvfile.isEnabled())
        self.assertTrue(self.form.files2analyze.isEnabled())

        self.assertFalse(self.form.btnCalculate.isEnabled())
        self.assertFalse(self.form.btnClear.isEnabled())
        # check boxes
        self.assertFalse(self.form.ChPeakHeight.isEnabled())
        self.assertFalse(self.form.ChPeakArea.isEnabled())
        self.assertFalse(self.form.ChBaseline.isEnabled())
        self.assertFalse(self.form.ChPeakPos.isEnabled())
        self.assertFalse(self.form.ChHead.isEnabled())
        self.assertFalse(self.form.ChPeakHeightRaw.isEnabled())
        # spins and bar
        self.assertFalse(self.form.DispSpin.isEnabled())
        self.assertFalse(self.form.DispFile.isEnabled())
        # TODO: Why is progressBar initially enabled?
        self.assertEqual(self.form.progressBar.isEnabled(), True)


    def test_defaults(self):
        """
        Testing the default states of the checkboxes and spins and lists

        Returns
        -------
        None.

        """
        #CheckBoxes
        self.assertEqual(self.form.ChPeakHeight.isChecked(), False)
        self.assertEqual(self.form.ChPeakArea.isChecked(), False)
        self.assertEqual(self.form.ChBaseline.isChecked(), False)
        self.assertEqual(self.form.ChPeakPos.isChecked(), False)
        self.assertEqual(self.form.ChHead.isChecked(), False)
        self.assertEqual(self.form.ChPeakHeightRaw.isChecked(), False)
        #Spinner
        self.assertEqual(self.form.DispSpin.value(), 0)
        #file list
        self.assertEqual(self.form.parent.model.stringList(), [])
        self.assertEqual(self.form.csvfile.text(), "")


    def test_setAll(self):
        """
        Checks if all the checkboxes are checked.
        Be aware of additional ones.

        Returns
        -------
        None.

        """
        self.form.set_all()
        self.checkboxesChecked()

    def test_setAll_withPreset(self):
        """
        Prevents toggeling effect

        Returns
        -------
        None.

        """
        self.form.ChPeakHeight.setChecked(True)
        self.form.ChPeakPos.setChecked(True)
        self.form.set_all()
        self.checkboxesChecked()

    def test_setFilename_reject(self):
        # checks if the form is visible
        self.assertTrue(self.form.isVisible())
        #preset the reject and accept threads
        esc = thrd.Thread(target=emu.key_reject)
        enter = thrd.Thread(target=emu.key_accept)
        # Open the dialog and reject it (start thread before open dialog)
        esc.start()
        QTest.mouseClick(self.form.btnSetFilename, Qt.LeftButton)
        #check if the button "Calculate" is not enabled
        self.assertFalse(self.form.btnCalculate.isEnabled(), "btnCalculate is enabled")
        #check if the parameters are not enabled
        self.checkboxesEnabled(False)

    def test_setFilename_accept(self):
        """
        Tests the behaviour of the setFilename button.
        Open of the dialog

        Returns
        -------
        None.

        """
        # checks if the form is visible
        self.assertTrue(self.form.isVisible())
        #preset the reject and accept threads
        esc = thrd.Thread(target=emu.key_reject)
        enter = thrd.Thread(target=emu.key_accept)
        # Open the dialog and accept it (start thread before open dialog)
        enter.start()
        QTest.mouseClick(self.form.btnSetFilename, Qt.LeftButton)
        # TODO: Check if a file is actually selected or batch.csv (preserved name) is acutally saved?
        #check if the button "Calculate" is enabled
        self.assertTrue(self.form.btnCalculate.isEnabled(), "btnCalculate is not enabled")
        #check if the parameters are enabled
        self.checkboxesEnabled()

    def checkboxesEnabled(self, enabled=True):
        """
        Tests whether all checkboxes of the parameter settings are enabled and
        also whether all checkboxes in the group BtnParameters are enabled.
        Hint: They should be similar, but changes may occur and that test will
        reveal it.

        Returns
        -------
        None.

        """
        self.assertEqual(self.form.ChPeakHeight.isEnabled(), enabled)
        self.assertEqual(self.form.ChPeakArea.isEnabled(), enabled)
        self.assertEqual(self.form.ChBaseline.isEnabled(), enabled)
        self.assertEqual(self.form.ChPeakPos.isEnabled(), enabled)
        self.assertEqual(self.form.ChHead.isEnabled(), enabled)
        self.assertEqual(self.form.ChPeakHeightRaw.isEnabled(), enabled)

        for button in self.form.BtnParameters.buttons():
            self.assertEqual(button.isEnabled(), enabled)

    def checkboxesChecked(self):
        """
        Tests whether all checkboxes of the parameter settings are checked and
        also whether all checkboxes in the group BtnParameters are checked.
        Hint: They should be similar, but changes may occur and that test will
        reveal it.

        Returns
        -------
        None.

        """
        self.assertTrue(self.form.ChPeakHeight.isChecked())
        self.assertTrue(self.form.ChPeakArea.isChecked())
        self.assertTrue(self.form.ChBaseline.isChecked())
        self.assertTrue(self.form.ChPeakPos.isChecked())
        self.assertTrue(self.form.ChHead.isChecked())
        self.assertTrue(self.form.ChPeakHeightRaw.isChecked())

        for button in self.form.BtnParameters.buttons():
            self.assertTrue(button.isChecked())
