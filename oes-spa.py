#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OES-Spectra-Analysis

Single and batch analysis of OES spectra
"""

# import pdb
# import re
import sys

import matplotlib as mpl
import numpy as np
from PyQt5.QtCore import QFileInfo, QStringListModel
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog,\
                            QMainWindow, QMessageBox

from ui.ui_main_window import Ui_main
# from ui.batch_dialog import Ui_batch
# import modules.data_handling as dtreat

mpl.use("Qt5Agg")

__author__ = "Peter Knittel"
__copyright__ = "Copyright 2019"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Peter Knittel"
__email__ = "peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"


def file_reader(filename):
    """Read out given files """

    # Check Filetype
    fileinfo = str(QFileInfo(filename).suffix())
    print(fileinfo)
    if fileinfo == "Spk" or fileinfo == "spk":
        # Get Data from tab separated ascii file
        print("eeeha")
        import csv
        csvreader = csv.reader(open(filename, 'r'), delimiter='\t',
                               quoting=csv.QUOTE_NONE)
        x_data = []
        y_data = []
        getdata = False
        csvtype = ""
        start = False
        for row in csvreader:
            if getdata:
                if csvtype == "pico":
                    x_data.append(float(row[1]))
                    y_data.append(float(row[2]))
                elif csvtype == "jpk":
                    if not row:
                        start = False
                        getdata = False
                    else:
                        if start:
                            jpkdata = row[0].split()
                            x_data.append(float(jpkdata[0]))
                            y_data.append(float(jpkdata[1]))
                        else:
                            start = True
            if row:
                if row[0] == "Time (s)":
                    getdata = True
                    csvtype = "pico"
                elif row[0] == "# units: m V s"\
                        or row[0] == "# units: m V V s":
                    getdata = True
                    csvtype = "jpk"

        return np.array(x_data), np.array(y_data)

    # Not supported Filetype
    return [0], [0]


class AnalysisWindow(QMainWindow):
    """Main Analysis Window Class """

    def __init__(self):
        QMainWindow.__init__(self)

        # Set lastdir
        self.lastdir = "./"

        # Set up the user interface from Designer.
        self.window = Ui_main()
        self.window.setupUi(self)
        self.sbar = self.statusBar()
        self.sbar.hide()
        self.setAcceptDrops(True)
        self.dropped_file = None
        self.widget = self.centralWidget()

        # Load multiple Dialog
        #self.batch = BatchAnalysis(self)

        # Setup Events MainWindow
        self.window.BtFileOpen.clicked.connect(self.file_open)
        self.window.ActionOpen.triggered.connect(self.file_open)
        self.window.BtRedraw.clicked.connect(self.redraw)
        self.window.ActionRedraw.triggered.connect(self.redraw)
        self.window.ActionSaveRaw.triggered.connect(self.save_raw)
        self.window.ActionSaveProcessed.triggered.connect(self.save_processed)
        #self.window.ActionAnalyzeMultipleFiles.triggered.\
            #connect(self.batch.show)

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
        np_x, np_y = file_reader(self.dropped_file)
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
            np_x, np_y = file_reader(filename)

            # Draw the spectra and print results
            self.draw_spectra(np_x, np_y)

    def draw_spectra(self, x_data, y_data):
        """Draw the raw spectrum and analyse it with DataHandler
        to obtain all parameters for the processed spectrum.
        """
        # Check whether data was found in the files
        if not x_data.any():
            self.window.redrawbtn.setEnabled(False)
            self.window.action_Redraw_spectra.setEnabled(False)
            QMessageBox.critical(self, "Error: File could not be opened",
                                 " Filetype unknown or file unreadable!")
            return 1

        # Enable Redraw Events
        self.window.redrawbtn.setEnabled(True)
        self.window.action_Redraw_spectra.setEnabled(True)

        # Clear the widget from previous spectra
        self.window.raw.axes.clear()
        self.window.fd.axes.clear()

        # Sent the raw data to the DataHandler and get parameters
        spec_analyse = dtreat.DataHandler(x_data, y_data)
        trace_x, trace_y = spec_analyse.getXY()
        p_trace_x, p_trace_y = spec_analyse.getProcessedXY()
        peak_height = spec_analyse.getPeakHeight(p_trace_x, p_trace_y)
        peak_area = spec_analyse.getPeakHeight(p_trace_x, p_trace_y)

        # Set Values obtained from DataHandler
        self.window.EdPeakHeight.setText(str(peak_height*1000000))
        self.window.EdPeakArea.setText(str(peak_area*1000000000))

        # Draw the spectra in MatPlotLibWidgets
        # Raw
        # self.window.raw.axes.hold(True)
        self.window.MplRaw.axes.set_xlabel(r"Pixel")
        self.window.MplRaw.axes.set_ylabel("Intensity / a.u.")
        self.window.MplRaw.axes.plot(trace_x, trace_y, "r")
        self.window.MplRaw.axes.legend(['Raw Spectrum'])
        self.window.MplRaw.axes.axhline(linewidth=0.5, color='0.2')
        self.window.MplRaw.axes.axvline(linewidth=0.5, color='0.2')
        self.window.MplRaw.draw()

        # Force-Distance spectrum
        # self.window.fd.axes.hold(True)
        self.window.MplProcessed.axes.set_xlabel(r"Wavelength / nm")
        self.window.MplProcessed.axes.set_ylabel("Intensity / a.u.")
        self.window.MplProcessed.axes.plot(p_trace_x,  p_trace_y, "r")
        self.window.MplProcessed.axes.legend(['Processed Spectrum'])
        self.window.MplProcessed.axes.axhline(linewidth=0.5, color='0.2')
        self.window.MplProcessed.axes.axvline(linewidth=0.5, color='0.2')
        self.window.MplProcessed.draw()

        self.window.menuSave.setEnabled(True)

        return 0

    def redraw(self):
        """Redraw the current spectrum selected """
        filename = str(self.window.EdFilename.text())
        if filename:
            x_data, y_data = file_reader(filename)
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
            csv_wr.writerow(["Raw data of:", str(self.window.EdFilename.text())])
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


# =============================================================================
# class BatchAnalysis(QDialog):
#     """Class for batch analysis. """
# 
#     def __init__(self, parent=None):
#         super(BatchAnalysis, self).__init__(parent)
# 
#         self.mui = Ui_batch()
#         self.mui.setupUi(self)
#         self.lastdir = parent.lastdir
#         self.model = QStringListModel()
#         self.mui.files2analyze.setModel(self.model)
# 
#         # Setup Events MultipleFiles
#         self.mui.setfilename.clicked.connect(self.set_filename)
#         self.mui.browseBtn.clicked.connect(self.set_spectra)
#         self.mui.clearBtn.clicked.connect(self.clear)
#         self.mui.calcBtn.clicked.connect(self.multi_calc)
#         self.mui.setfilename.clicked.connect(self.set_filename)
#         self.mui.files2analyze.clicked.connect(self.get_list_index)
#         self.mui.DispSpin.valueChanged.connect(self.disp_curve)
#         # self.connect(self.mui.files2analyze, SIGNAL('clicked(QModelIndex)'),
#         #              self.get_list_index)
#         # self.connect(self.mui.DispSpin, SIGNAL('valueChanged(int)'),
#         #              self.disp_curve)
# 
#     def dragEnterEvent(self, event):
#         """Drag file over window event """
#         if event.mimeData().hasUrls():
#             for url in event.mimeData().urls():
#                 if url.isValid():
#                     if url.scheme() == "file":
#                         self.files.append(url.toLocalFile())
#                         event.accept()
# 
#     def dropEvent(self, _event):
#         """Dropping File """
#         self.model.setStringList(self.files)
#         self.mui.files2analyze.setModel(self.model)
#         self.mui.clearBtn.setEnabled(True)
# 
#     def set_filename(self):
#         """Handling target filename """
#         filename, _ = QFileDialog.getSaveFileName(self, 'Set Filename',
#                                                   self.lastdir,
#                                                   "Comma separated (*.csv)")
#         if str(filename) != "":
#             if QFileInfo(filename).suffix() != "csv":
#                 filename = filename+".csv"
#             self.lastdir = str(QFileInfo(filename).absolutePath())
#             self.mui.csvfile.setText(filename)
#             self.mui.browseBtn.setEnabled(True)
#             if self.model.stringList():
#                 self.mui.calcBtn.setEnabled(True)
#                 self.mui.groupBox.setEnabled(True)
#                 self.mui.clearBtn.setEnabled(True)
# 
#     def set_spectra(self):
#         """Handling source filesnames """
#         filenames, _ = QFileDialog.getOpenFileNames(
#             self, 'Choose Files to analyze',
#             self.lastdir, "PicoView File (*.mi);;\
#             Ascii (tab separated)(*.txt);;Bruker or other(*.*)")
# 
#         if int(len(filenames)) != 0:
#             self.model.setStringList(filenames)
#             self.mui.calcBtn.setEnabled(True)
#             self.mui.groupBox.setEnabled(True)
#             self.mui.clearBtn.setEnabled(True)
#             self.mui.DispSpin.setEnabled(True)
#             self.mui.DispSpin.setMaximum(int(len(filenames)-1))
#             self.mui.DispFile.setEnabled(True)
#             self.mui.files2analyze.setCurrentIndex(self.model.index(0))
#             self.mui.DispFile.setText(QFileInfo(filenames[0]).fileName())
#             self.parent().file_open(filenames[0])
#             self.mui.files2analyze.setModel(self.model)
# 
#     def clear(self):
#         """Reset UI """
#         self.mui.calcBtn.setEnabled(False)
#         self.mui.groupBox.setEnabled(False)
#         self.mui.clearBtn.setEnabled(False)
#         self.mui.DispSpin.setEnabled(False)
#         self.mui.DispSpin.setValue(0)
#         self.mui.DispFile.setEnabled(False)
#         self.model.setStringList("")
#         self.mui.files2analyze.setModel(self.model)
# 
#     def multi_calc(self):
#         """Batch process spectra and write to CSV """
#         csvfile = str(self.mui.csvfile.text())
#         s_adhforce = self.mui.adhforce.checkState()
#         s_adhwork = self.mui.adhwork.checkState()
#         s_elasticity = self.mui.elasticity.checkState()
#         s_contact = self.mui.contact.checkState()
#         s_indent = self.mui.indent.checkState()
#         self.model = self.mui.files2analyze.model()
#         filenames = self.model.stringList()
#         amount = int(len(filenames))
# 
#         import csv
#         # Set correct Filename and open it
#         myfile = open(csvfile, 'w')
# 
#         # Open CSV-Writer Instance and write data in Excel dialect
#         csv_wr = csv.writer(myfile, dialect=csv.excel, quoting=csv.QUOTE_NONE)
#         header = ["Filename:"]
#         if s_adhforce == 2:
#             header.append("Adhesion Force (nN):")
#         if s_adhwork == 2:
#             header.append("Adhesion Work (const_kbt):")
#         if s_elasticity == 2:
#             header.append("Elasticity(Pa):")
#         if s_contact == 2:
#             header.append("Contact Point (um):")
#         if s_indent == 2:
#             header.append("Indentation (nm):")
# 
#         csv_wr.writerow(header)
#         i = 0
#         while i < amount:
#             file = str(filenames[i])
#             data_x, data_y = file_reader(file)
#             self.mui.progressBar.setValue(int(float((i+1))/float(amount)*100))
# 
#             fd_analyse = dtreat.DataHandler(data_x, data_y)
#             row = [file]
# 
#             if s_adhforce == 2:
#                 vadforce = fd_analyse.MaxAdhesionForce()*1000000000
#                 row.append(vadforce)
#             if s_adhwork == 2:
#                 const_kbt = 1.3806488e-23 * (293.15)
#                 vadwork = fd_analyse.AdhesionWork()/const_kbt
#                 row.append(vadwork)
#             if s_elasticity == 2:
#                 elasticity = fd_analyse.getElasticity()
#                 row.append(elasticity)
#             if s_contact == 2:
#                 c_point = fd_analyse.ContactPoint()*1000000
#                 row.append(c_point)
#             if s_indent == 2:
#                 indent = fd_analyse.MaxIndentation()*1000000000
#                 row.append(indent)
#             csv_wr.writerow(row)
#             i += 1
# 
#         self.mui.progressBar.setValue(100)
#         myfile.close()
# 
#     def disp_curve(self, value):
#         """Display curve with selected index in MainWindow """
#         self.model = self.mui.files2analyze.model()
#         self.mui.files2analyze.setCurrentIndex(self.model.index(value))
#         filenames = self.model.stringList()
#         self.mui.DispFile.setText(QFileInfo(filenames[value]).fileName())
#         self.parent().file_open(filenames[value])
# 
#     def get_list_index(self, index):
#         """Get Current selected file by index """
#         self.mui.files2analyze.setCurrentIndex(index)
#         self.mui.DispSpin.setValue(index.row())
# =============================================================================


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
