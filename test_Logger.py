#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 09:01:08 2020

@author: hauke
"""


# standard libs
import sys
import unittest

# libs
from Logger import Logger

class TestLoadFiles(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Setting up the corresponding variables
        """
        # prequerities
        cls.logger = Logger(__name__)


    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_init(self):
        """Checking whether an object was instaciated"""
        self.assertTrue(self.logger, "no instance of logger found!")

        """Checking whether the default settings are ok"""
        self.assertEqual(self.logger.logger.getEffectiveLevel(), 10, "Default logging level (DEBUG)")


    def test_messages(self):
        # testing the module and its behaviour
        self.logger.debug("Debugging Nachricht")
        self.logger.info("Info Nachricht")
        self.logger.warning("Warnung")
        self.logger.error("Error Nachricht")
        self.logger.critical("Kritische Nachricht")

    def test_filename(self):
        # set LOG_FILE in config.yml to arbitraryFilename
        arbitraryFilename = "arbitraryFilename"

        # Checks whether the filename was loaded correctly.
        self.assertEqual(self.logger.filename, arbitraryFilename,
                         "Arbitrary filename from config")




if __name__ == '__main__':
    unittest.main()
