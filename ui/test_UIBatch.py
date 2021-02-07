#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 11:59:03 2020

@author: Hauke Wernecke
"""

# standard libs
import sys
import unittest

# third-party libs
import emulator as emu
import threading as THR
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# local modules/libs
from modules.AnalysisWindow import AnalysisWindow


class TestUIBatch(unittest.TestCase):


    @classmethod
    def setUp(self):
        """
        Setting up the ui and the corresponding variables
        """
        # UI
        self.app = QApplication(sys.argv)
        self.window = AnalysisWindow()
        # # display the uis
        self.window.show()
        self.window.batch.show()
        # # variables
        self.batch = self.window.batch
        self.form = self.window.batch._window


    @classmethod
    def tearDown(self):
        # close the window if something raises an error
        self.batch.close()
        self.window.close()



    def test_availability(self):
        """
        Test wheter elements are default enabled.

        Returns
        -------
        None.

        """
        self.assertTrue(self.form.btnSetFilename.isEnabled())
        self.assertTrue(self.form.btnBrowse.isEnabled())
        self.assertTrue(self.form.foutBatchfile.isEnabled())
        self.assertTrue(self.form.listFiles.isEnabled())

        self.assertTrue(self.form.btnClear.isEnabled())
        # check boxes
        self.assertTrue(self.form.cbPeakHeight.isEnabled())
        self.assertTrue(self.form.cbPeakArea.isEnabled())
        self.assertTrue(self.form.cbBaseline.isEnabled())
        self.assertTrue(self.form.cbPeakPos.isEnabled())
        self.assertTrue(self.form.cbHead.isEnabled())
        self.assertTrue(self.form.barProgress.isEnabled())

        self.assertFalse(self.form.btnAnalyze.isEnabled())


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
        #file list
        self.assertEqual(self.form.parent.model.stringList(), [])
        self.assertEqual(self.form.foutBatchfile.text(), "")

    def test_propUpdatePlots_default(self):
        """Testing the default values of property and ui"""
        checkbox = self.form.cbUpdatePlots.isChecked()
        prop = self.batch.updatePlots
        self.assertEqual(checkbox, prop)

    def test_propUpdatePlots_setUI(self):
        """setting the UI and then testing if they are equal"""
        self.form.cbUpdatePlots.setChecked(True)
        # self.form.cbUpdatePlots.click()
        checkbox = self.form.cbUpdatePlots.isChecked()
        prop = self.batch.updatePlots
        self.assertEqual(checkbox, prop)

    def test_propUpdatePlots_setProp(self):
        """setting the UI and then testing if they are equal"""
        self.batch.updatePlots = True
        checkbox = self.form.cbUpdatePlots.isChecked()
        prop = self.batch.updatePlots
        self.assertEqual(checkbox, prop)



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
        esc = THR.Thread(target=emu.key_reject)
        # Open the dialog and reject it (start thread before open dialog)
        esc.start()
        QTest.mouseClick(self.form.btnSetFilename, Qt.LeftButton)
        #check if the button "Calculate" is not enabled
        self.assertFalse(self.form.btnAnalyze.isEnabled(), "btnAnalyze is enabled")

    def test_setFilename_accept(self):
        """
        Tests the behaviour of the setFilename button.
        Open of the dialog

        Returns
        -------
        None.

        """
        #preset the accept thread
        enter = THR.Thread(target=emu.key_accept)
        # Open the dialog and accept it (start thread before open dialog)
        enter.start()
        # confirm override if file already exists
        yes = THR.Thread(target=emu.key_alt_j)
        yes.start()
        QTest.mouseClick(self.form.btnSetFilename, Qt.LeftButton)
        # TODO: Check if a file is actually selected or batch.csv (preserved name) is acutally saved?
        #check if the button "Calculate" is enabled
        #self.assertTrue(self.form.btnAnalyze.isEnabled(), "btnAnalyze is not enabled")

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

if __name__ == '__main__':
    unittest.main()
