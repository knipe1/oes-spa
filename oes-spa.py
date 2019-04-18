#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OES-Spectra-Analysis

Single and batch analysis of OES spectra
"""

# import pdb
# import re
import sys

import matplotlib as mpl
# import numpy as np
from PyQt5.QtCore import QFileInfo, QStringListModel
from PyQt5.QtWidgets import QApplication, QFileDialog,\
                            QMainWindow, QMessageBox, QDialog

from ui.ui_main_window import Ui_main
from ui.ui_batch_dialog import Ui_batch

import modules.file_reader as r_file
import modules.data_processing as dproc

mpl.use("Qt5Agg")

__author__ = "Peter Knittel"
__copyright__ = "Copyright 2019"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Peter Knittel"
__email__ = "peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"


class AnalysisWindow(QMainWindow):
    """Main Analysis Window Class """

    def __init__(self):
        QMainWindow.__init__(self)

        # Set lastdir
        self.lastdir = "./"
        self.openFile = ""

        # Set up the user interface from Designer.
        self.window = Ui_main()
        self.window.setupUi(self)
        self.sbar = self.statusBar()
        self.sbar.hide()
        self.setAcceptDrops(True)
        self.dropped_file = None
        self.widget = self.centralWidget()

        # Load batch dialog
        self.batch = BatchAnalysis(self)

        # Setup Events MainWindow
        self.window.BtFileOpen.clicked.connect(self.file_open)
        self.window.ActionOpen.triggered.connect(self.file_open)
        self.window.BtRedraw.clicked.connect(self.redraw)
        self.window.ActionRedraw.triggered.connect(self.redraw)
        self.window.ActionSaveRaw.triggered.connect(self.save_raw)
        self.window.ActionSaveProcessed.triggered.connect(self.save_processed)
        self.window.ActionAnalyzeMultipleFiles.triggered.\
            connect(self.batch.show)

    def dragEnterEvent(self, event):
        """Drag Element over Window """
        self.dropped_file = None
        if event.mimeData().hasUrls():
            if len(event.mimeData().urls()) > 1:
                self.batch.show()
            else:
                url = event.mimeData().urls()[0]
                if url.isValid():
                    if url.scheme() == "file":
                        self.dropped_file = url.toLocalFile()
                        event.accept()

    def dropEvent(self, _event):
        """Dropping File """
        self.window.EdFilename.setText(self.dropped_file)
        self.openFile = r_file.FileReader(self.dropped_file)
        np_x, np_y = self.openFile.get_values()
        self.window.menuSave.setEnabled(False)
        self.draw_spectra(np_x, np_y)

    def file_open(self, filename):
        """Open FileDialog to choose Raw-Data-File """
        if filename is False:
            filename, _ = QFileDialog.getOpenFileName(
                self.widget, 'Load File', self.lastdir,
                "SpexHex File (*.spk);;Exported Raw spectrum (*.csv)")
        else:
            filename = filename

        if str(filename) != "":
            self.window.menuSave.setEnabled(False)
            self.window.EdFilename.setText(filename)
            self.lastdir = str(QFileInfo(filename).absolutePath())
            # Read out the chosen file
            self.openFile = r_file.FileReader(filename)
            np_x, np_y = self.openFile.get_values()

            # Draw the spectra and print results
            self.draw_spectra(np_x, np_y)

    def draw_spectra(self, x_data, y_data):
        """Draw the raw spectrum and analyse it with DataHandler
        to obtain all parameters for the processed spectrum.
        """
        # Check whether data was found in the files
        if not x_data.any():
            self.window.BtRedraw.setEnabled(False)
            self.window.ActionRedraw.setEnabled(False)
            QMessageBox.critical(self, "Error: File could not be opened",
                                 " Filetype unknown or file unreadable!")
            return 1

        # Enable Redraw Events
        self.window.BtRedraw.setEnabled(True)
        self.window.ActionRedraw.setEnabled(True)

        # Clear the widget from previous spectra
        self.window.MplRaw.axes.clear()
        self.window.MplProcessed.axes.clear()

        # Sent the raw data to the DataHandler and get parameters
        spec_proc = dproc.DataHandler(
                        x_data, y_data,
                        float(self.window.EdCWavelength.text()),
                        int(self.window.GratingBox.currentText()))
        procX, procY = spec_proc.get_processed_data()
        baseline, avg = spec_proc.get_baseline()
        self.window.EdBaseline.setText(str(avg))
        peak_height, peak_area = spec_proc.get_peak()
        self.window.EdPeakHeight.setText(str(peak_height))
        self.window.EdPeakArea.setText(str(peak_area))

        # Draw the spectra in MatPlotLibWidgets
        # Raw
        self.window.MplRaw.axes.set_xlabel(r"Pixel")
        self.window.MplRaw.axes.set_ylabel("Intensity / a.u.")
        self.window.MplRaw.axes.plot(x_data, y_data, "r")
        self.window.MplRaw.axes.plot(x_data, baseline, "b--")
        self.window.MplRaw.axes.legend(['Raw Spectrum', 'Baseline'])
        self.window.MplRaw.axes.axhline(linewidth=0.5, color='0.2')
        self.window.MplRaw.axes.axvline(linewidth=0.5, color='0.2')
        self.window.MplRaw.draw()

        # Processed
        self.window.MplProcessed.axes.set_xlabel(r"Wavelength / nm")
        self.window.MplProcessed.axes.set_ylabel("Intensity / a.u.")
        self.window.MplProcessed.axes.plot(procX, procY, "r")
        self.window.MplProcessed.axes.set_xlim(procX[0], procX[-1])
        self.window.MplProcessed.axes.legend(['Processed Spectrum'])
        self.window.MplProcessed.axes.axhline(linewidth=0.5, color='0.2')
        self.window.MplProcessed.axes.axvline(linewidth=0.5, color='0.2')
        # self.window.MplProcessed.axes.autoscale(True, 'both', True)
        self.window.MplProcessed.draw()

        self.window.menuSave.setEnabled(True)

        return 0

    def redraw(self):
        """Redraw the current spectrum selected """
        filename = str(self.window.EdFilename.text())
        if filename:
            x_data, y_data = self.openFile.get_values()
            self.draw_spectra(x_data, y_data)
        else:
            QMessageBox.warning(self.widget, "Warning", "No File selected!")

    def save_raw(self, filename):
        """Save Raw-Data in CSV-File """
        if not filename:
            filename, _ = QFileDialog.getSaveFileName(
                self.widget, 'Save raw spectrum to...',
                self.lastdir, "Comma separated (*.csv)")

        if str(filename) != "":
            if QFileInfo(filename).suffix() != "csv":
                filename = filename+".csv"
            self.lastdir = str(QFileInfo(filename).absolutePath())

            import csv
            if sys.version_info >= (3, 0, 0):
                myfile = open(filename, 'w', newline='')
            else:
                myfile = open(filename, 'wb')

            # Open CSV-Writer Instance and write data in Excel dialect
            csv_wr = csv.writer(myfile, dialect=csv.excel,
                                quoting=csv.QUOTE_NONE)
            csv_wr.writerow(["Raw data of:",
                             str(self.window.EdFilename.text())])
            csv_wr.writerow("")
            csv_wr.writerow(["Pixel", "Intensity"])
            csv_wr.writerow("")
            csv_wr.writerow(["Data:"])
            csv_wr.writerow("")
            for i in range(0, len(self.raw_xtrace_drawn), 1)[::-1]:
                csv_wr.writerow([self.raw_xtrace_drawn[i]] +
                                [self.raw_ytrace_drawn[i]])

            myfile.close()

    def save_processed(self, filename):
        """Save processed spectrum to CSV-File """
        if not filename:
            filename, _ = QFileDialog.getSaveFileName(
                self.widget,
                'Save processed spectrum to...',
                self.lastdir, "Comma separated (*.csv)")

        if str(filename) != "":
            if QFileInfo(filename).suffix() != "csv":
                filename = filename + ".csv"
            self.lastdir = str(QFileInfo(filename).absolutePath())

            import csv
            if sys.version_info >= (3, 0, 0):
                myfile = open(filename, 'w', newline='')
            else:
                myfile = open(filename, 'wb')

            # Open CSV-Writer Instance and write data in Excel dialect
            csv_wr = csv.writer(myfile, dialect=csv.excel,
                                quoting=csv.QUOTE_NONE)
            csv_wr.writerow(["Processed Spectrum of:",
                             str(self.window.EdFilename.text())])
            csv_wr.writerow("")
            csv_wr.writerow(["Wavelength / nm", "Intensity / a.u."])
            csv_wr.writerow("")
            csv_wr.writerow(["Data:"])
            csv_wr.writerow("")
            for i in range(0, len(self.fd_xtrace_drawn), 1)[::-1]:
                csv_wr.writerow([self.fd_xtrace_drawn[i]] +
                                [self.fd_ytrace_drawn[i]])

            myfile.close()


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
        self.mui.DispSpin.setMaximum(int(len(self.files)-1))
        self.mui.DispFile.setEnabled(True)
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
        filenames, _ = QFileDialog.getOpenFileNames(
            self, 'Choose Files to analyze',
            self.lastdir, "SpexHex File (*.spk)")

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


def main():
    """Main program """

    # Setup GUI
    app = QApplication(sys.argv)
    window = AnalysisWindow()

    # Show Window
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
