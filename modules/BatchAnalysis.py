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
from PyQt5.QtWidgets import QDialog

from ui.UIBatch import UIBatch

import modules.FileReader as r_file
import modules.DataHandler as dproc
import modules.Universal as uni
import dialog_messages as dialog

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

        self.setAcceptDrops(True)
        self.files = []
        self.lastdir = parent.lastdir
        self.model = QStringListModel()
        # init of mui has to be at last, because it connects self.model i.a.
        self.mui = UIBatch(self)


    def dragEnterEvent(self, event):
        """Drag file over window event """
        # TODO: purpose?
        # If just one url has the scheme "file" the event is accepted
#        if event.mimeData().hasUrls():
#            for url in event.mimeData().urls():
#                if url.isValid() and url.scheme() == "file":
#                    self.files.append(url.toLocalFile())
#                    event.accept()
#        """alternative?!
        urls = event.mimeData().urls();
        for url in urls:
            if url.scheme() == "file":
                event.accept()
#        """

    def dropEvent(self, event):
        """Dropping File """
        urls = event.mimeData().urls();
        for url in urls:
            if uni.is_valid_filetype(self, url):
                self.files.append(url.toLocalFile())
        self.accept_files();
#        self.model.setStringList(self.files)
#        self.mui.DispSpin.setMaximum(int(len(self.files)-1)) # TODO: typecast unneccessary
#        self.mui.DispSpin.setMaximum(len(self.files)-1) # TODO: typecast unneccessary
        self.enable_UI(True)
        self.mui.listFiles.setCurrentIndex(self.model.index(0))
        self.mui.DispFile.setText(QFileInfo(self.files[0]).fileName())
        self.parent().file_open(self.files[0])

    def set_filename(self):
        """Handling target filename """
        filename = dialog.dialog_saveFile(self.lastdir, parent=self)
        if str(filename) != "":
            if QFileInfo(filename).suffix() != "csv":
                filename = filename+".csv"
            self.lastdir = str(QFileInfo(filename).absolutePath())
            self.mui.foutCSV.setText(filename)
#            self.mui.browseBtn.setEnabled(True)
            if self.model.stringList():
                self.enable_UI(True)

    def set_spectra(self):
        """Handling source filesnames """
#        filenames = uni.load_files(self.lastdir);
        self.files =  uni.load_files(self.lastdir);
#        filenames, _ = QFileDialog.getOpenFileNames(
#            self, 'Choose Files to analyze',
#            self.lastdir, "SpexHex File (*.spk)")

        if len(self.files) != 0:
            self.accept_files();
#            self.model.setStringList(self.files)

            self.enable_UI(True)
#            self.mui.DispSpin.setMaximum(int(len(filenames)-1))
            self.mui.listFiles.setCurrentIndex(self.model.index(0))
            self.mui.DispFile.setText(QFileInfo(self.files[0]).fileName())
            self.parent().file_open(self.files[0])
#            self.mui.listFiles.setModel(self.model)

    def clear(self):
        """Reset UI """
#        self.mui.DispSpin.setValue(0)
#        self.model.setStringList([])
        self.clear_files();
        self.enable_UI(False)

    def multi_calc(self):
        """Batch process spectra and write to CSV """
        csvfile = str(self.mui.foutCSV.text())
        s_peak_height = self.mui.ChPeakHeight.checkState()
        s_peak_area = self.mui.ChPeakArea.checkState()
        s_baseline = self.mui.ChBaseline.checkState()
        s_peak_position = self.mui.ChPeakPos.checkState()
        s_peak_height_raw = self.mui.ChPeakHeightRaw.checkState()
        s_head = self.mui.ChHead.checkState()
#        self.model = self.mui.listFiles.model() # TODO: doesn't change at anny given time
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
        # TODO: Why while-loop? Why no for-loop?
        i = 0
        while i < amount:
            # Progress
            self.set_progressBar(float(i+1)/float(amount))

            # Read out the file
            file = str(filenames[i])
            self.openFile = r_file.FileReader(file)
            data_x, data_y = self.openFile.get_values()
            time, date = self.openFile.get_head()

            # Get Parameters
            spec_proc = dproc.DataHandler(
                        data_x, data_y,
                        float(self.parent().window.tinCentralWavelength.text()),
                        int(self.parent().window.ddGrating.currentText()))
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

        myfile.close()

    def disp_curve(self, value):
        """Display curve with selected index in MainWindow """
#        self.model = self.mui.listFiles.model() # TODO: doesn't change at anny given time
        self.mui.listFiles.setCurrentIndex(self.model.index(value))
        filenames = self.model.stringList()
        self.mui.DispFile.setText(QFileInfo(filenames[value]).fileName())
        self.parent().file_open(filenames[value])

    def get_list_index(self, index):
        """Get Current selected file by index """
        self.mui.listFiles.setCurrentIndex(index)
        self.mui.DispSpin.setValue(index.row())

    def set_progressBar(self, percentage):
        """sets hte percentage to the progress bar"""
        self.mui.progressBar.setValue(int(percentage*100))
        return 0;

    def enable_UI(self, enable):
        """enable/disable elements if files/no file is in the list"""
        self.mui.boxParameter.setEnabled(enable)
        [elem.setEnabled(enable) for elem in self.mui.groupDisplay.children()]
        [btn.setEnabled(enable) for btn in self.mui.btnFileaction.buttons()]

    def accept_files(self):
        """setting the list of files and the maximum index"""
        numerOfFiles = len(self.files);
        self.model.setStringList(self.files)
        if numerOfFiles < 0:
            self.mui.DispSpin.setMaximum(0)
        else:
            self.mui.DispSpin.setMaximum(numerOfFiles-1)

    def clear_files(self):
        """setting the list of files and the maximum index"""
        self.files =  []
        self.accept_files()