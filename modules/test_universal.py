# -*- coding: utf-8 -*-
import unittest
import sys

from universal import load_files

from PyQt5.QtCore import QFileInfo, QStringListModel
from PyQt5.QtWidgets import QApplication, QFileDialog,\
                            QMainWindow, QMessageBox, QDialog

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
        
        singleSpkFile = load_files(self.spkFile_1)[0];
        singleCsvFile = load_files(self.csvFile_1)[0];
        singleDocxFile = load_files(self.textfile_2)[0];
        multDataFiles = load_files(self.multSpk);
        
        
        self.assertAlmostEqual(singleSpkFile, self.spkFile_1);
        self.assertAlmostEqual(singleCsvFile, self.csvFile_1);
        self.assertAlmostEqual(singleDocxFile, self.textfile_2);
        
    def test_values(self):
        self.assertRaises(TypeError, load_files, 12);
        self.assertRaises(TypeError, load_files, ["asd", 12]);
        self.assertRaises(TypeError, load_files, 3.4);