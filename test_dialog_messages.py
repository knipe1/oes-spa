#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Still a lot of untested code.
If errors occur, extend this file to test the issue.

Created on August 17th 2021

Testing the dialogs.
This is rather a manual test!

@author: Hauke Wernecke
"""

# third-party imports
import sys
import unittest

# imports

# third-party classes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow

# classes
import dialog_messages as dialog




import unittest

class TestLoadFiles(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # UI
        cls.app = QApplication(sys.argv)
        cls.window = QMainWindow()

    @classmethod
    def tearDownClass(cls):
        # close the window if something raises an error
        cls.window.close()


    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_critical_invalidSpectrum(self):
        dialog.critical_invalidSpectrum()


    def test_dialog_watchdogDirectory(self):
        # Cancel
        self.assertEqual(dialog.dialog_watchdogDirectory(), "")
        # Select any directory
        self.assertNotEqual(dialog.dialog_watchdogDirectory(), "")
        # Select another directory -> compare the entry points of the dialog
        self.assertNotEqual(dialog.dialog_watchdogDirectory(), "")


    def test_dialog_importBatchfile(self):
        # Cancel
        self.assertEqual(dialog.dialog_importBatchfile(), "")
        # Select any file
        self.assertNotEqual(dialog.dialog_importBatchfile(), "")
        # -> compare the entry points of the dialog
        self.assertNotEqual(dialog.dialog_importBatchfile(), "")


    def test_dialog_batchfile(self):
        # Cancel
        self.assertEqual(dialog.dialog_batchfile(), "")
        # Select any file
        self.assertNotEqual(dialog.dialog_batchfile(), "")
        # -> compare the entry points of the dialog
        self.assertNotEqual(dialog.dialog_batchfile(), "")






if __name__ == '__main__':
    unittest.main()
