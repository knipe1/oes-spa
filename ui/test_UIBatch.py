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
        self.assertTrue(self.form.foutCSV.isEnabled())
        self.assertTrue(self.form.listFiles.isEnabled())

        self.assertFalse(self.form.btnCalculate.isEnabled())
        self.assertFalse(self.form.btnClear.isEnabled())
        # check boxes
        self.assertFalse(self.form.cbPeakHeight.isEnabled())
        self.assertFalse(self.form.cbPeakArea.isEnabled())
        self.assertFalse(self.form.cbBaseline.isEnabled())
        self.assertFalse(self.form.cbPeakPos.isEnabled())
        self.assertFalse(self.form.cbHead.isEnabled())
        # spins and bar
        # self.assertFalse(self.form.DispSpin.isEnabled())
        # self.assertFalse(self.form.DispFile.isEnabled())
        # TODO: Why is barProcess initially enabled?
        self.assertEqual(self.form.barProcess.isEnabled(), True)


    def test_defaults(self):
        """
        Testing the default states of the checkboxes and spins and lists

        Returns
        -------
        None.

        """
        #CheckBoxes
        self.assertEqual(self.form.cbPeakHeight.isChecked(), False)
        self.assertEqual(self.form.cbPeakArea.isChecked(), False)
        self.assertEqual(self.form.cbBaseline.isChecked(), False)
        self.assertEqual(self.form.cbPeakPos.isChecked(), False)
        self.assertEqual(self.form.cbHead.isChecked(), False)
        #Spinner
        self.assertEqual(self.form.DispSpin.value(), 0)
        #file list
        self.assertEqual(self.form.parent.model.stringList(), [])
        self.assertEqual(self.form.foutCSV.text(), "")


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
        self.form.cbPeakHeight.setChecked(True)
        self.form.cbPeakPos.setChecked(True)
        self.form.set_all()
        self.checkboxesChecked()

    def test_setFilename_reject(self):
        # checks if the form is visible
        # self.assertTrue(self.form.isVisible())
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
        # self.assertTrue(self.form.isVisible())
        #preset the reject and accept threads
        esc = thrd.Thread(target=emu.key_reject)
        enter = thrd.Thread(target=emu.key_accept)
        # Open the dialog and accept it (start thread before open dialog)
        enter.start()
        QTest.mouseClick(self.form.btnSetFilename, Qt.LeftButton)
        # TODO: Check if a file is actually selected or batch.csv (preserved name) is acutally saved?
        #check if the button "Calculate" is enabled
        #self.assertTrue(self.form.btnCalculate.isEnabled(), "btnCalculate is not enabled")
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
        self.assertEqual(self.form.cbPeakHeight.isEnabled(), enabled)
        self.assertEqual(self.form.cbPeakArea.isEnabled(), enabled)
        self.assertEqual(self.form.cbBaseline.isEnabled(), enabled)
        self.assertEqual(self.form.cbPeakPos.isEnabled(), enabled)
        self.assertEqual(self.form.cbHead.isEnabled(), enabled)

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
        self.assertTrue(self.form.cbPeakHeight.isChecked())
        self.assertTrue(self.form.cbPeakArea.isChecked())
        self.assertTrue(self.form.cbBaseline.isChecked())
        self.assertTrue(self.form.cbPeakPos.isChecked())
        self.assertTrue(self.form.cbHead.isChecked())

        for button in self.form.BtnParameters.buttons():
            self.assertTrue(button.isChecked())
