# -*- coding: utf-8 -*-
import unittest
import sys

from modules.Universal import load_files
from modules.Universal import reduce_path
from modules.Universal import add_index_to_text

from PyQt5.QtCore import QFileInfo, QStringListModel
from PyQt5.QtWidgets import QApplication, QFileDialog,\
                            QMainWindow, QMessageBox, QDialog

import emulator as emu
import threading as thrd

class TestLoadFiles(unittest.TestCase):
    def setUp(self):
        # Setup GUI
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()

        # Show Window
        self.window.show()
        #sys.exit(app.exec_())

        # prequerities
        self.csvFile_1 = "H:/OES/__oes-spectra-analysis/modules/testfiles/csvfile_1.csv";
        self.spkFile_1 = "H:/OES/__oes-spectra-analysis/modules/testfiles/spkfile_1.Spk";
        self.spkFile_2 = "H:/OES/__oes-spectra-analysis/modules/testfiles/spkfile_2.spk";
        self.textfile_2 = "H:/OES/__oes-spectra-analysis/modules/testfiles/textfile.docx";
        self.multSpk = 'H:/OES/__oes-spectra-analysis/modules/testfiles/"spkfile_1.Spk" "spkfile_2.spk"';

    def test_loadfiles(self):
        enter = thrd.Thread(target=emu.key_accept)
                # Open the dialog and reject it (start thread before open dialog)
        enter.start()
        singleSpkFile = load_files(self.spkFile_1)[0];
        enter = thrd.Thread(target=emu.key_accept)
        enter.start()
        singleCsvFile = load_files(self.csvFile_1)[0];
        enter = thrd.Thread(target=emu.key_accept)
        enter.start()
        singleDocxFile = load_files(self.textfile_2)[0];
        enter = thrd.Thread(target=emu.key_accept)
        enter.start()
        multDataFiles = load_files(self.multSpk);


        self.assertAlmostEqual(singleSpkFile, self.spkFile_1);
        self.assertAlmostEqual(singleCsvFile, self.csvFile_1);
        self.assertAlmostEqual(singleDocxFile, self.textfile_2);

    def test_values(self):
        self.assertRaises(TypeError, load_files, 12);
        self.assertRaises(TypeError, load_files, ["asd", 12]);
        self.assertRaises(TypeError, load_files, 3.4);

class TestReducePath(unittest.TestCase):
    def setUp(self):
        # normal urls
        self.url = "H:/OES/__oes-spectra-analysis/modules/testfiles/csvfile_1.csv";
        self.shortUrl = "H:/csvfile_1.csv"
        self.filenameUrl = "csvfile_1.csv"
        self.listUrl = [self.url, self.shortUrl, self.filenameUrl]
        # reduced urls
        self.reducedUrl = reduce_path(self.url)
        self.reducedShortUrl = reduce_path(self.shortUrl)
        self.reducedFilenameUrl = reduce_path(self.filenameUrl)


    def test_ok_reducePath(self):
        # urls
        self.assertEqual(self.reducedUrl, "/testfiles/csvfile_1.csv")
        self.assertEqual(self.reducedShortUrl, "H:/csvfile_1.csv")
        self.assertEqual(self.reducedFilenameUrl, "csvfile_1.csv")
        # list of urls
        self.assertEqual(type(reduce_path(self.listUrl)), list)

    def test_raise_reducePath(self):
        self.assertRaises(TypeError, reduce_path, 12);
        self.assertRaises(TypeError, reduce_path, ["asd", 12]);
        self.assertRaises(TypeError, reduce_path, 3.4);
        self.assertRaises(TypeError, reduce_path, (3.4, "asd"));


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

