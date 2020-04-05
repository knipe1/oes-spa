#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

__author__ = "Peter Knittel"
__copyright__ = "Copyright 2019"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Peter Knittel/ Hauke Wernecke"
__email__ = "peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"


# standard libs
#import matplotlib as mpl

# third-party libs
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QMainWindow

# local modules/libs
import modules.Universal as uni
import dialog_messages as dialog
from modules.BatchAnalysis import BatchAnalysis
from modules.DataHandler import DataHandler
from modules.FileReader import FileReader
from modules.FileWriter import FileWriter
from modules.Universal import ExportType
from ui.UIMain import UIMain


config = uni.load_config()
# plots
PLOT = config["PLOT"];
# filesystem
FILE = config["FILE"]
<<<<<<< HEAD
# load properties
LOAD = config["LOAD"]
||||||| merged common ancestors
# filesystem
LOAD = config["LOAD"]
=======
# filesystem
IMPORT = config["IMPORT"]
>>>>>>> WER_overview



class AnalysisWindow(QMainWindow):
    """Main Analysis Window Class """

    def __init__(self, initialShow=True):
        """initialize the parent class ( == QMainWindow.__init__(self)"""
        super(AnalysisWindow, self).__init__()

        # Set file and directory
        self.lastdir = FILE["DEF_DIR"];
        self.openFile = FILE["DEF_FILE"];
        # general settings
        # TODO: maybe false, if BatchAnalysis is open?
        self.setAcceptDrops(True)
<<<<<<< HEAD
        # TODO: comment?
        self.widget = self.centralWidget()
||||||| merged common ancestors
        self.widget = self.centralWidget()
=======
        # TODO: Usage? self.centralWidget() return None and is never used.
        # self.widget = self.centralWidget()
>>>>>>> WER_overview

        # Set up the user interface from Designer.
        # Load batch dialog
        self.batch = BatchAnalysis(self)
        # Load the main window (uses self.batch already)
        self.window = UIMain(self)
        
        # initial settings
        if initialShow:
            self.show()
            
    def closeEvent(self, event):
        """
        Closing the BatchAnalysis dialog to have a clear shutdown.

        Parameters
        ----------
        event : event
            close event of the main window.

        Returns
        -------
        None.

        """
        self.batch.close()

    def dragEnterEvent(self, event):
        """Drag Element over Window """
        # event.accept --> dropEvent is handled by Widget not by BatchAnalysis

        #Prequerities
        urls = event.mimeData().urls();

        if len(urls) > 1:
            self.batch.show();
        elif len(urls) == 1:
            # TODO: only check the first one? different schemes possible?
            url = urls[0];
<<<<<<< HEAD
            # TODO: see also uni.is_valid_filetype
            if url.isValid() and url.scheme() in LOAD["VALID_SCHEME"]:
||||||| merged common ancestors
            if url.isValid() and url.scheme() in LOAD["VALID_SCHEME"]:
=======
            if url.isValid() and url.scheme() in IMPORT["VALID_SCHEME"]:
>>>>>>> WER_overview
                event.accept()


    def dropEvent(self, event):
		# TODO: ought be a function and in the event handler just a function call, right?
        """Dropping File """
        # can only be one single file.
        # TODO: errorhandling?
        url = event.mimeData().urls()[0];
        # TODO: why doublecheck (see above)
        if uni.is_valid_filetype(self, url):
            self.apply_data(url.toLocalFile())
            event.accept();

    def file_open(self, files):
        """Open FileDialog to choose Raw-Data-File """
        # Load a file via menu bar
        # File-->Open
        # Batch-->Drag&Drop or -->Browse Files
<<<<<<< HEAD
        # TODO: Check cases in which filename is False/True something else
        # TODO: rename filename into files
        if filename is False:
            filename = uni.load_files(self.lastdir);
            # TODO: implement multi proc
            if len(filename) > 0:
                self.batch.show();
                self.batch.update_filelist(filename)
            elif len(filename) == 1:
                filename = filename[0];
||||||| merged common ancestors
        if filename is False:
            filename = uni.load_files(self.lastdir);
            # TODO: implement multi proc
            if filename:
                filename = filename[0];
=======
        if files is False:
            files = uni.load_files(self.lastdir);
            if len(files) > 1:
                self.batch.show();
                self.batch.update_filelist(files)
            elif len(files) == 1:
                files = files[0];
>>>>>>> WER_overview
            else:
                files = "";


        if files != "":
            #str() for typecast from utf16(Qstring) to utf8(python string)
<<<<<<< HEAD
            # TODO: neccesary
            self.lastdir = str(QFileInfo(filename).absolutePath())
||||||| merged common ancestors
            self.lastdir = str(QFileInfo(filename).absolutePath())
=======
            self.lastdir = str(QFileInfo(files).absolutePath())
>>>>>>> WER_overview

            self.apply_data(files)

    def draw_spectra(self, x_data, y_data):
        """Draw the raw spectrum and analyze it with DataHandler
        to obtain all parameters for the processed spectrum.
        """
        # Check whether data was found in the files
        if not x_data.any():
            # TODO: obsolet?
            self.plot_redrawable(False)
            dialog.critical_unknownFiletype(self)
            return 1

        # Sent the raw data to the DataHandler and get parameters
        # TODO: function required for getting parameters and errorhandling!
        # TODO: Is Central wavelength depending on the selected Fitting?
        spec_proc = DataHandler(x_data, y_data,
                        float(self.window.tinCentralWavelength.text()),
                        int(self.window.ddGrating.currentText()))
        #calculate results
        # TODO: no validation of results?
        procX, procY = spec_proc.get_processed_data()
        baseline, avg = spec_proc.get_baseline()
        peak_height, peak_area = spec_proc.get_peak()

        # display results
        # TODO: expected behaviour? What happens if not everything is given?
        # Is there a scenario in which just one result is calculated/set?
        self.window.toutBaseline.setText(str(avg))
        self.window.toutPeakHeight.setText(str(peak_height))
        self.window.toutPeakArea.setText(str(peak_area))

        # Clear the widget from previous spectra
        # Draw the spectra in MatPlotLibWidgets
        # Raw
        rawPlot = self.window.mplRaw;
        self.init_plot(rawPlot, PLOT["RAW_X_LABEL"], PLOT["RAW_Y_LABEL"]);
        self.update_plot(rawPlot, x_data, y_data,
                         PLOT["RAW_DATA_MRK"], PLOT["RAW_DATA_LABEL"]);
        self.update_plot(rawPlot, x_data, baseline,
                         PLOT["RAW_BASELINE_MRK"], PLOT["RAW_BASELINE_LABEL"]);

        # Processed
        processedPlot = self.window.mplProcessed;
        self.init_plot(processedPlot, PLOT["PROCESSED_X_LABEL"], PLOT["PROCESSED_Y_LABEL"]);
        self.update_plot(processedPlot, procX, procY,
                         PLOT["PROCESSED_DATA_MRK"], PLOT["PROCESSED_DATA_LABEL"]);


        # Enable Redraw Events
        # TODO: obsolet?
        self.plot_redrawable(True)

        return 0

<<<<<<< HEAD
    # TODO: obsolet????
    def redraw(self):
        """Redraw the current spectrum selected """
        # TODO: separate elements for displaying information and input elements
        # --> new class attribute for self.activeFile,
        #   which is set, whenever something is drawn
        # is it openfile?
        # --> and update the displayed filename
        filename = str(self.window.toutFilename.text())
        if filename:
            x_data, y_data = self.openFile.get_values()
            self.draw_spectra(x_data, y_data)
        else:
            dialog.warning_fileSelection(self.widget)
||||||| merged common ancestors
    def redraw(self):
        """Redraw the current spectrum selected """
        # TODO: separate elements for displaying information and input elements
        # --> new class attribute for self.activeFile,
        #   which is set, whenever something is drawn
        # is it openfile?
        # --> and update the displayed filename
        filename = str(self.window.toutFilename.text())
        if filename:
            x_data, y_data = self.openFile.get_values()
            self.draw_spectra(x_data, y_data)
        else:
            dialog.warning_fileSelection(self.widget)
=======
    # def redraw(self):
    #     """Redraw the current spectrum selected """
    #     # TODO: separate elements for displaying information and input elements
    #     # --> new class attribute for self.activeFile,
    #     #   which is set, whenever something is drawn
    #     # is it openfile?
    #     # --> and update the displayed filename
    #     filename = str(self.window.toutFilename.text())
    #     if filename:
    #         x_data, y_data = self.openFile.get_values()
    #         self.draw_spectra(x_data, y_data)
    #     else:
    #         # dialog.warning_fileSelection(self.widget)
    #         dialog.warning_fileSelection()
>>>>>>> WER_overview

    def save_raw(self, filename):
        """Save Raw-Data in CSV-File """
        # collect data
        filename, timestamp = self.get_fileinformation()
        labels = [PLOT["RAW_X_LABEL"], PLOT["RAW_Y_LABEL"]]
        xyData = uni.extract_xy_data(self.window.mplRaw.axes,
                                     PLOT["RAW_DATA_LABEL"])
        # write data to csv
        csvWriter = FileWriter(self, filename, timestamp)
        csvWriter.write_data(xyData, labels, ExportType.RAW)
        return 0;

    def save_processed(self, filename):
        """Save processed spectrum to CSV-File """
        # collect data
        filename, timestamp = self.get_fileinformation()
        labels = [PLOT["PROCESSED_X_LABEL"], PLOT["PROCESSED_Y_LABEL"]]
        xyData = uni.extract_xy_data(self.window.mplProcessed.axes,
                                     PLOT["PROCESSED_DATA_LABEL"])

        results = {}
        # TODO: use enum?
        results["Peak Height"] = self.window.toutPeakHeight.text()
        results["Peak Area"] = self.window.toutPeakArea.text()

        # write data to csv
        csvWriter = FileWriter(self, filename, timestamp)
        csvWriter.write_data(xyData, labels, ExportType.PROCESSED, results)
        return 0;

    def init_plot(self, plotObj, xlabel, ylabel):
        # TODO: errorhandling
        """Gets a plot object and label it after clearing it"""
        plotObj.axes.clear();
        plotObj.axes.set_xlabel(xlabel);
        plotObj.axes.set_ylabel(ylabel);
        plotObj.axes.axhline(linewidth=PLOT["DEF_LINEWIDTH"],
                             color=PLOT["DEF_AXIS_COLOR"]);
        plotObj.axes.axvline(linewidth=PLOT["DEF_LINEWIDTH"],
                             color=PLOT["DEF_AXIS_COLOR"]);
        return 0;


    def update_plot(self, plotObj, xData, yData, color, label):
        """updates a given plot"""
        # TODO: errorhandling
        plotObj.axes.plot(xData, yData, color, label=label);
        plotObj.axes.set_xlim(xData[0], xData[-1]);
        plotObj.axes.legend();
        plotObj.draw();
        return 0;


    def plot_redrawable(self, enable = True):
        """set the status (enabled/disabled) of redraw button/action"""
        self.window.actRedraw.setEnabled(enable);
        # menu --> File --> save
        # TODO: but important!!!
        self.window.menuSave.setEnabled(enable)
        return 0;

    def get_fileinformation(self):
        # TODO: self.file
        # TODO: self.timestamp
        # TODO: self.file = {name: asd, timestamp: sad}
        filename = self.window.toutFilename.text()
        date = self.window.toutDate.text()
        time = self.window.toutTime.text()
        timestamp = date + " " + time
        return filename, timestamp

    def set_fileinformation(self, filename, date, time):
        # TODO: date+time = timestamp?
        """set the file information (filename, date and time)"""
        # validate inputs
        # TODO: try catch?
        if type(filename) not in [str]:
            raise TypeError("date must be of type string")
        if type(date) not in [str]:
            raise TypeError("date must be of type string")
        if type(time) not in [str]:
            raise TypeError("time must be of type string")

        # set values
        self.window.toutFilename.setText(filename)
        self.window.toutDate.setText(date)
        self.window.toutTime.setText(time)
        return 0

    def apply_data(self, filename):
        """read out a file and extract its information,
        then set header information and draw spectra"""
        # TODO: error handling
        # Read out the chosen file
        self.openFile = FileReader(filename)
        np_x, np_y = self.openFile.get_values()
        time, date = self.openFile.get_head()
        # Draw the spectra and print results
        if not (time and date and np_x.size and np_y.size):
            return 1
        self.set_fileinformation(filename, date, time)
        self.draw_spectra(np_x, np_y)
        return 0
