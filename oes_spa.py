#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OES-Spectra-Analysis

Single and batch analysis of OES spectra
"""

import sys

import matplotlib as mpl
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QApplication, QFileDialog,\
                            QMainWindow, QMessageBox

from ui.ui_main_window import Ui_main

import modules.FileReader as r_file
import modules.DataHandler as dproc
import modules.Universal as uni
import modules.BatchAnalysis as batch

# set interactive backend
mpl.use("Qt5Agg")

__author__ = "Peter Knittel"
__copyright__ = "Copyright 2019"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Peter Knittel"
__email__ = "peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"


# parameters
# DEF --> Default
# DIR --> directory
# r+string --> raw string, no special characters like \n, \t,...


# plots
RAW_DATA_LABEL = "Raw Spectrum";
RAW_DATA_MRK = "r"
RAW_BASELINE_LABEL = "Baseline";
RAW_BASELINE_MRK = "b--";
RAW_X_LABEL = r"Pixel";
RAW_Y_LABEL = r"Intensity / a.u.";
PROCESSED_DATA_LABEL = "Processed Spectrum";
PROCESSED_DATA_MRK = RAW_DATA_MRK;
PROCESSED_X_LABEL = r"Wavelength / nm";
PROCESSED_Y_LABEL = RAW_Y_LABEL;
DEF_LINEWIDTH = 0.5;
DEF_AXIS_COLOR = '0.2';

# filesystem
DEF_DIR = "./";
DEF_FILE = "";

       



class AnalysisWindow(QMainWindow):
    """Main Analysis Window Class """

    def __init__(self):
        QMainWindow.__init__(self)

        # Set file and directory
        self.lastdir = DEF_DIR;
        self.openFile = DEF_FILE;

        # Set up the user interface from Designer.
        self.window = Ui_main()
        self.window.setupUi(self)
        self.sbar = self.statusBar()
        self.sbar.hide()
        self.setAcceptDrops(True)
        self.droppedFile = None
        self.widget = self.centralWidget()

        # Load batch dialog
        self.batch = batch.BatchAnalysis(self)

        # Setup Events MainWindow
        # Action: option in a dropdown of the menu bar
        # Bt : Button
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
        # event.accept --> dropEvent is handled by Widget not by BatchAnalysis
        
        #Prequerities
        validScheme = ["file"];                 
        urls = event.mimeData().urls();
        
        if len(urls) > 1:
            self.batch.show();
        elif len(urls) == 1:
            # TODO: only check the first one? different schemes possible?
            url = urls[0];
            if url.isValid() and url.scheme() in validScheme:
                event.accept()
            else:
                event.ignore();
        else:
            event.ignore();
    

    def dropEvent(self, event):
		# TODO: ought be a function and in the event handler just a function call, right?
        """Dropping File """
        url = event.mimeData().urls()[0];
        if uni.is_valid_filetype(self,url):
            self.droppedFile = url.toLocalFile();
            self.apply_data(self.droppedFile)
        else:
            event.ignore();
        
        
        # get information
        # TODO: validate information (return value)
#        self.openFile = r_file.FileReader(self.droppedFile)
#        np_x, np_y = self.openFile.get_values()
#        time, date = self.openFile.get_head()
#        
#        #set information
#        self.set_fileinformation(self.droppedFile, date, time)
#        self.draw_spectra(np_x, np_y)

    def file_open(self, filename):
        """Open FileDialog to choose Raw-Data-File """
        # Load a file via menu bar
        # File-->Open
        # Batch-->Drag&Drop or -->Browse Files
        if filename is False:
            filename = uni.LoadFiles(self.lastdir);
            # TODO: implement multi proc
            filename = filename[0];
#            filename, _ = QFileDialog.getOpenFileName(
#                self.widget, 'Load File', self.lastdir,
#                "SpexHex File (*.spk);;Exported Raw spectrum (*.csv)")		#magic

        if filename != "":
            #str() for typecast from utf16(Qstring) to utf8(python string)
            self.lastdir = str(QFileInfo(filename).absolutePath()) 
            
            self.apply_data(filename)
#            # Read out the chosen file
#            self.openFile = r_file.FileReader(filename)
#            np_x, np_y = self.openFile.get_values()
#            time, date = self.openFile.get_head()
#
#            # Draw the spectra and print results
#            self.set_fileinformation(filename, date, time)
#            self.draw_spectra(np_x, np_y)

    def draw_spectra(self, x_data, y_data):
        """Draw the raw spectrum and analyse it with DataHandler
        to obtain all parameters for the processed spectrum.
        """
        # Check whether data was found in the files
        if not x_data.any():
            self.plot_redrawable(False)
            self.window.menuSave.setEnabled(False)
            QMessageBox.critical(self, "Error: File could not be opened",
                                 " Filetype unknown or file unreadable!")
            return 1

        # Enable Redraw Events
        self.plot_redrawable(True)

        # Sent the raw data to the DataHandler and get parameters
        # TODO: function required for getting parameters and errorhandling!
        # TODO: Is Central wavelength depending on the selected Fitting?
        spec_proc = dproc.DataHandler(x_data, y_data,
                        float(self.window.EdCWavelength.text()),
                        int(self.window.GratingBox.currentText()))
        #calculate results
        # TODO: no validation of results?
        procX, procY = spec_proc.get_processed_data()
        baseline, avg = spec_proc.get_baseline()
        peak_height, peak_area = spec_proc.get_peak()
        
        # display results
        # TODO: expected behaviour? What happens if not everything is given? 
        # Is there a scenario in which just one result is calculated/set?
        self.window.EdBaseline.setText(str(avg))
        self.window.EdPeakHeight.setText(str(peak_height))
        self.window.EdPeakArea.setText(str(peak_area))

        # Clear the widget from previous spectra
        # Draw the spectra in MatPlotLibWidgets
        # Raw
        rawPlot = self.window.MplRaw;
        self.init_plot(rawPlot, RAW_X_LABEL, RAW_Y_LABEL);
        self.update_plot(rawPlot, x_data, y_data, 
                         RAW_DATA_MRK, RAW_DATA_LABEL);
        self.update_plot(rawPlot, x_data, baseline, 
                         RAW_BASELINE_MRK, RAW_BASELINE_LABEL);

        # Processed
        processedPlot = self.window.MplProcessed;
        self.init_plot(processedPlot, PROCESSED_X_LABEL, PROCESSED_Y_LABEL);
        self.update_plot(processedPlot, procX, procY, 
                         PROCESSED_DATA_MRK, PROCESSED_DATA_LABEL);

        # TODO: What does it mean? What is it good for?
        # menu --> File --> save
        self.window.menuSave.setEnabled(True)
                
        return 0

    def redraw(self):
        """Redraw the current spectrum selected """
        # TODO: separate elements for displaying information and input elements
        # --> new class attribute for self.activeFile, 
        #   which is set, whenever something is drawn
        # is it openfile?
        # --> and update the displayed filename
        filename = str(self.window.EdFilename.text())
        if filename:
            x_data, y_data = self.openFile.get_values()
            self.draw_spectra(x_data, y_data)
        else:
            QMessageBox.warning(self.widget, "Warning", "No File selected!")		#magic

    def save_raw(self, filename):
        """Save Raw-Data in CSV-File """
        if not filename:
            # TODO: repetition
            filename, _ = QFileDialog.getSaveFileName(
                self.widget, 'Save raw spectrum to...',
                self.lastdir, "Comma separated (*.csv)")

        if str(filename) != "":		#magic
            if QFileInfo(filename).suffix() != "csv":		#magic
                filename = filename+".csv"		#magic
            self.lastdir = str(QFileInfo(filename).absolutePath())

            import csv
            if sys.version_info >= (3, 0, 0):		#magic
                myfile = open(filename, 'w', newline='')		#magic
            else:
                myfile = open(filename, 'wb')		#magic

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
            # TODO: repetition
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
            
    
    def init_plot(self, plotObj, xlabel, ylabel):
        """Gets a plot object and label it after clearing it"""
        plotObj.axes.clear();
        plotObj.axes.set_xlabel(xlabel);
        plotObj.axes.set_ylabel(ylabel);
        plotObj.axes.axhline(linewidth=DEF_LINEWIDTH, color=DEF_AXIS_COLOR);
        plotObj.axes.axvline(linewidth=DEF_LINEWIDTH, color=DEF_AXIS_COLOR);
        return 0;
    
    
    def update_plot(self, plotObj, xData, yData, color, label):
        """updates a given plot"""
        plotObj.axes.plot(xData, yData, color, label=label);
        plotObj.axes.set_xlim(xData[0], xData[-1]);
        plotObj.axes.legend();
        plotObj.draw();
        return 0;
        
    
    def plot_redrawable(self, enable = True):
        """set the status (enabled/disabled) of redraw button/action"""
        self.window.BtRedraw.setEnabled(enable);
        self.window.ActionRedraw.setEnabled(enable);
        return 0;
    
    
    def set_fileinformation(self, filename, date, time):
        """set the file information (filename, date and time)"""
        # validate inputs
        if type(filename) not in [str]:
            raise TypeError("date must be of type string")
        if type(date) not in [str]:
            raise TypeError("date must be of type string")
        if type(time) not in [str]:
            raise TypeError("time must be of type string")
        
        # set values
        self.window.EdFilename.setText(filename)
        self.window.EdDate.setText(date)
        self.window.EdTime.setText(time)
        return 0
    
    
#    def is_valid_filetype(self, url):
#        """checks if the given url is valid to load the data"""
#        isValid = True;
#        file = url.toLocalFile();
#        
#        if not url.isValid():
#            isValid = False;
#        
#        if QFileInfo(file).completeSuffix().lower() in VALID_FILE_SUFFIX:
#            self.droppedFile = file;
#        else:
#            isValid = False;
#            # TODO: magic strings?
#            strSuffixes = ["." + suffix for suffix in VALID_FILE_SUFFIX];
#            strSuffixes = ", ".join(strSuffixes);
#            QMessageBox.critical(self, "Error: File could not be opened",
#                         f"Valid filetypes: {strSuffixes}");
#        return isValid;
    
    def apply_data(self, filename):
        """read out a file and extract its information, 
        then set header information and draw spectra"""
        # TODO: error handling
        # Read out the chosen file
        self.openFile = r_file.FileReader(filename)
        np_x, np_y = self.openFile.get_values()
        time, date = self.openFile.get_head()

        # Draw the spectra and print results
        self.set_fileinformation(filename, date, time)
        self.draw_spectra(np_x, np_y)
        return 0

def main():
    """Main program """

    # Setup GUI
    app = QApplication(sys.argv)
    window = AnalysisWindow()

    # Show Window
    window.show()
    sys.exit(app.exec_())


# compatibility to python 2? 
# in Py3 you just need main() without the if statement
if __name__ == '__main__':
    main()
