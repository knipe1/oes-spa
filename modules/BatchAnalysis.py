# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 10:22:44 2020

@author: Wernecke
"""

"""
Batch-Analysis

Batch analysis of OES spectra
"""

import matplotlib as mpl
from PyQt5.QtCore import QFileInfo, QStringListModel
from PyQt5.QtWidgets import QFileDialog, QDialog

from ui.ui_batch_dialog import Ui_batch

import modules.FileReader as r_file
import modules.DataHandler as dproc
import modules.Universal as uni

# set interactive backend
mpl.use("Qt5Agg")

__author__ = "Hauke Wernecke"
__copyright__ = "Copyright 2020"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Hauke Wernecke/Peter Knittel"
__email__ = "hauke.wernecke@iaf.fraunhhofer.de, peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"

class BatchAnalysis(QDialog):
    """Class for batch analysis. """

    def __init__(self, parent=None):
        super(BatchAnalysis, self).__init__(parent)

        self.mui = Ui_batch()
        self.mui.setupUi(self)
        self.setAcceptDrops(True)
        self.files = []
        self.lastdir = parent.lastdir
        self.model = QStringListModel()
        self.mui.files2analyze.setModel(self.model)

        # Setup Events MultipleFiles
        self.mui.setfilename.clicked.connect(self.set_filename)
        self.mui.browseBtn.clicked.connect(self.set_spectra)
        self.mui.clearBtn.clicked.connect(self.clear)
        self.mui.calcBtn.clicked.connect(self.multi_calc)
# =============================================================================
#         self.mui.files2analyze.selectionModel().selectionChanged.connect(
#                 self.get_list_index)
# =============================================================================
        self.mui.files2analyze.clicked.connect(
                self.get_list_index)
        self.mui.DispSpin.valueChanged.connect(self.disp_curve)
        
        
        self.mui.browseBtn.setEnabled(True)

    def dragEnterEvent(self, event):
        """Drag file over window event """
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isValid():
                    if url.scheme() == "file":
                        self.files.append(url.toLocalFile())
                        event.accept()

    def dropEvent(self, _event):
        """Dropping File """
        self.model.setStringList(self.files)
        self.mui.files2analyze.setModel(self.model)
        self.mui.clearBtn.setEnabled(True)
        self.mui.DispSpin.setEnabled(True)
        self.mui.DispSpin.setMaximum(int(len(self.files)-1)) # TODO: typecast unneccessary
        self.mui.DispFile.setEnabled(True)
        self.mui.calcBtn.setEnabled(True)
        self.mui.groupBox.setEnabled(True)
        self.mui.files2analyze.setCurrentIndex(self.model.index(0))
        self.mui.DispFile.setText(QFileInfo(self.files[0]).fileName())
        self.parent().file_open(self.files[0])

    def set_filename(self):
        """Handling target filename """
        filename, _ = QFileDialog.getSaveFileName(self, 'Set Filename',
                                                  self.lastdir,
                                                  "Comma separated (*.csv)")
        if str(filename) != "":
            if QFileInfo(filename).suffix() != "csv":
                filename = filename+".csv"
            self.lastdir = str(QFileInfo(filename).absolutePath())
            self.mui.csvfile.setText(filename)
            self.mui.browseBtn.setEnabled(True)
            if self.model.stringList():
                self.mui.calcBtn.setEnabled(True)
                self.mui.groupBox.setEnabled(True)
                self.mui.clearBtn.setEnabled(True)

    def set_spectra(self):
        """Handling source filesnames """
        filenames = uni.LoadFiles(self.lastdir);
#        filenames, _ = QFileDialog.getOpenFileNames(
#            self, 'Choose Files to analyze',
#            self.lastdir, "SpexHex File (*.spk)")

        if int(len(filenames)) != 0:
            self.model.setStringList(filenames)
            self.mui.calcBtn.setEnabled(True)
            self.mui.groupBox.setEnabled(True)
            self.mui.clearBtn.setEnabled(True)
            self.mui.DispSpin.setEnabled(True)
            self.mui.DispSpin.setMaximum(int(len(filenames)-1))
            self.mui.DispFile.setEnabled(True)
            self.mui.files2analyze.setCurrentIndex(self.model.index(0))
            self.mui.DispFile.setText(QFileInfo(filenames[0]).fileName())
            self.parent().file_open(filenames[0])
            self.mui.files2analyze.setModel(self.model)

    def clear(self):
        """Reset UI """
        self.mui.calcBtn.setEnabled(False)
        self.mui.groupBox.setEnabled(False)
        self.mui.clearBtn.setEnabled(False)
        self.mui.DispSpin.setEnabled(False)
        self.mui.DispSpin.setValue(0)
        self.mui.DispFile.setEnabled(False)
        self.model.setStringList([])
        self.mui.files2analyze.setModel(self.model)

    def multi_calc(self):
        """Batch process spectra and write to CSV """
        csvfile = str(self.mui.csvfile.text())
        s_peak_height = self.mui.ChPeakHeight.checkState()
        s_peak_area = self.mui.ChPeakArea.checkState()
        s_baseline = self.mui.ChBaseline.checkState()
        s_peak_position = self.mui.ChPeakPos.checkState()
        s_peak_height_raw = self.mui.ChPeakHeightRaw.checkState()
        s_head = self.mui.ChHead.checkState()
        self.model = self.mui.files2analyze.model()
        filenames = self.model.stringList()
        amount = int(len(filenames))

        import csv
        # Set correct Filename and open it
        myfile = open(csvfile, 'w')

        # Open CSV-Writer Instance and write data in Excel dialect
        csv_wr = csv.writer(myfile, dialect=csv.excel, quoting=csv.QUOTE_NONE)
        header = ["Filename:"]
        if s_peak_height == 2:
            header.append("Peak height:")
        if s_peak_area == 2:
            header.append("Peak area:")
        if s_baseline == 2:
            header.append("Baseline:")
        if s_peak_position == 2:
            header.append("Peak position:")
        if s_head == 2:
            header.append("Header info:")
        if s_peak_height_raw == 2:
            header.append("Peak height (not corrected):")

        csv_wr.writerow(header)
        i = 0
        while i < amount:
            # Progress
            self.mui.progressBar.setValue(int(float((i+1))/float(amount)*100))

            # Read out the file
            file = str(filenames[i])
            self.openFile = r_file.FileReader(file)
            data_x, data_y = self.openFile.get_values()
            time, date = self.openFile.get_head()

            # Get Parameters
            spec_proc = dproc.DataHandler(
                        data_x, data_y,
                        float(self.parent().window.EdCWavelength.text()),
                        int(self.parent().window.GratingBox.currentText()))
            procX, procY = spec_proc.get_processed_data()
            baseline, avg = spec_proc.get_baseline()
            peak_height, peak_area = spec_proc.get_peak()
            peak_position, peak_raw = spec_proc.get_peak_raw()

            row = [file]

            if s_peak_height == 2:
                row.append(peak_height)
            if s_peak_area == 2:
                row.append(peak_area)
            if s_baseline == 2:
                row.append(avg)
            if s_peak_position == 2:
                row.append(peak_position)
            if s_head == 2:
                row.append(date + " " + time)
            if s_peak_height_raw == 2:
                row.append(peak_raw)

            csv_wr.writerow(row)
            i += 1

        self.mui.progressBar.setValue(100)
        myfile.close()

    def disp_curve(self, value):
        """Display curve with selected index in MainWindow """
        self.model = self.mui.files2analyze.model()
        self.mui.files2analyze.setCurrentIndex(self.model.index(value))
        filenames = self.model.stringList()
        self.mui.DispFile.setText(QFileInfo(filenames[value]).fileName())
        self.parent().file_open(filenames[value])

    def get_list_index(self, index):
        """Get Current selected file by index """
        self.mui.files2analyze.setCurrentIndex(index)
        self.mui.DispSpin.setValue(index.row())