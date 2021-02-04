#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Hauke Wernecke
"""



# standard libs
import sys
import unittest

# third-party libs
import emulator as emu
import threading as THR
from PyQt5.QtCore import QFileInfo

# local modules/libs
from modules.Universal import reduce_paths
from modules.Universal import add_index_to_text

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

    # def test_loadfiles(self):
    #     # Open the dialog and reject it (start thread before open dialog)
    #     enter = THR.Thread(target=emu.key_accept)
    #     enter.start()
    #     singleSpkFile = load_files(self.spkFile_1)[0];
    #     enter = THR.Thread(target=emu.key_accept)
    #     enter.start()
    #     singleCsvFile = load_files(self.csvFile_1)[0];
    #     enter = THR.Thread(target=emu.key_accept)
    #     enter.start()
    #     singleDocxFile = load_files(self.textfile_2)[0];
    #     enter = THR.Thread(target=emu.key_accept)
    #     enter.start()
    #     multDataFiles = load_files(self.multSpk);

    #     self.assertEqual(singleSpkFile, self.spkFile_1, "Spk-File");
    #     self.assertEqual(singleCsvFile, self.csvFile_1, "Csv-File");
    #     self.assertEqual(singleDocxFile, self.textfile_2, "Docx-File");
    #     self.assertEqual(len(multDataFiles), 2, "Multiple Files");

    # def test_values(self):
    #     with self.assertRaises(TypeError):
    #         load_files(12)
    #         load_files(["asd", 12])
    #         load_files(3.4)

class TestReducePath(unittest.TestCase):
    def setUp(self):
        # normal urls
        self.url = "./modules/testfiles/csvfile_1.csv";
        self.shortUrl = "H:/csvfile_1.csv"
        self.filenameUrl = "csvfile_1.csv"
        self.listUrl = [self.url, self.shortUrl, self.filenameUrl]
        # reduced urls
        self.reducedUrl = reduce_paths(self.url)
        self.reducedShortUrl = reduce_paths(self.shortUrl)
        self.reducedFilenameUrl = reduce_paths(self.filenameUrl)


    def test_ok_reducePath(self):
        # urls
        self.assertEqual(self.reducedUrl, "/testfiles/csvfile_1.csv")
        self.assertEqual(self.reducedShortUrl, "H:/csvfile_1.csv")
        self.assertEqual(self.reducedFilenameUrl, "csvfile_1.csv")
        # list of urls
        self.assertEqual(type(reduce_paths(self.listUrl)), list)

    def test_raise_reducePath(self):
        self.assertRaises(TypeError, reduce_paths, 12);
        self.assertRaises(TypeError, reduce_paths, ["asd", 12]);
        self.assertRaises(TypeError, reduce_paths, 3.4);
        self.assertRaises(TypeError, reduce_paths, (3.4, "asd"));


class TestAddIndexToText(unittest.TestCase):
    def setUp(self):
        # valid entries
        self.stringlist = ["a", "b", "c", "d", "e", "f"]
        # invalid variables
        self.list = [3, "a"]
        self.number = 12123

    def test_ok_addIndexToText(self):
        self.assertEqual(add_index_to_text(self.stringlist),
                          ["   0:a",
                          "   1:b",
                          "   2:c",
                          "   3:d",
                          "   4:e",
                          "   5:f"])

    def test_raise_addIndexToText(self):
        self.assertRaises(TypeError, add_index_to_text, self.list);
        self.assertRaises(TypeError, add_index_to_text, self.number);


if __name__ == '__main__':
    unittest.main()
