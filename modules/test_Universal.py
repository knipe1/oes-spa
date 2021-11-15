#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Hauke Wernecke
"""



# standard libs
import sys
import unittest
import numpy as np
from datetime import datetime

# third-party libs
import emulator as emu
import threading as THR
from PyQt5.QtCore import QFileInfo

# local modules/libs
import modules.universal as uni


class TestLoadFiles(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Setting up the corresponding variables
        """
        # prequerities
        # path
        path = "./modules/testfiles/"
        path = QFileInfo(path).absolutePath() + "/"
        # files
        cls.csvFile_1 = path + "csvfile_1.csv";
        cls.spkFile_1 = path + "spkfile_1.Spk";
        cls.spkFile_2 = path + "spkfile_2.spk";
        cls.textfile_2 = path + "textfile.docx";
        cls.multSpk = path + '"spkfile_1.Spk" "spkfile_2.spk"';


    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass
    def tearDown(self):
        pass


class TestReducePath(unittest.TestCase):
    def setUp(self):
        # normal urls
        self.url = "./modules/testfiles/csvfile_1.csv"
        self.shortUrl = "H:/csvfile_1.csv"
        self.filenameUrl = "csvfile_1.csv"
        self.listUrl = [self.url, self.shortUrl, self.filenameUrl]
        # reduced urls
        self.reducedUrl = uni.reduce_path(self.url)
        self.reducedShortUrl = uni.reduce_path(self.shortUrl)
        self.reducedFilenameUrl = uni.reduce_path(self.filenameUrl)


    def test_ok_reducePath(self):
        # urls
        self.assertEqual(self.reducedUrl, "testfiles/csvfile_1.csv")
        self.assertEqual(self.reducedShortUrl, "H:/csvfile_1.csv")
        self.assertEqual(self.reducedFilenameUrl, "oes-spectra-analysis-Homeversion/csvfile_1.csv")


class TestConvertToTime(unittest.TestCase):
    # Signature
    # convert_to_time(data:np.ndarray)->np.ndarray:
    def setUp(self):
        timeList = [datetime.now() for _ in range(50)]
        self.datetimeArray = np.asarray(timeList)
        self.stringArray = np.asarray([uni.timestamp_to_string(t) for t in self.datetimeArray.copy()])


    def test_convert_from_datetime(self):
        self.assertTrue(all(self.datetimeArray == uni.convert_to_time(self.datetimeArray)))


    def test_convert_from_string(self):
        converted = uni.convert_to_time(self.stringArray)
        self.assertTrue(all((isinstance(t, datetime) for t in converted)))


    def test_remove_None_from_iterable(self):
        t = (1, 2, "A", "B", None, [34, None])
        l = list(t)
        for iterable in (t, l):
            self.assertFalse(None in uni.remove_None_from_iterable(iterable))



if __name__ == '__main__':
    unittest.main()
