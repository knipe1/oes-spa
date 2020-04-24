#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Hauke Wernecke
"""


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
from modules.Fitting import Fitting
from modules.Universal import ExportType
from ui.UIMain import UIMain



class AnalysisWindow(QMainWindow):
    """
    Main Window. Organization and interfaces of sub-types/windows.


    Further descriptions...

    Usage:


    Attributes
    ----------
    name : type
        description.


    Methods
    -------
    """

    config = uni.load_config()
    # plots
    PLOT = config["PLOT"];
    # filesystem
    FILE = config["FILE"]
    # load properties
    IMPORT = config["IMPORT"]

    def __init__(self, initialShow=True):
        """initialize the parent class ( == QMainWindow.__init__(self)"""
        super(AnalysisWindow, self).__init__()

        # Set file and directory
        self.lastdir = self.FILE["DEF_DIR"];
        self.openFile = self.FILE["DEF_FILE"];
        # general settings
        # TODO: maybe false, if BatchAnalysis is open?
        self.setAcceptDrops(True)
        # TODO: Usage? self.centralWidget() return None and is never used.
        # self.widget = self.centralWidget()


        # Set up the user interface from Designer.
        # Load the main window
        self.window = UIMain(self)
        # Load batch dialog
        self.batch = BatchAnalysis(self)
        # init the fitting and with the retrieved fittings
        self.fittings = Fitting(self.window.fittings)

        self.__post_init__()

        # initial settings
        if initialShow:
            self.show()

    def __post_init__(self):
        self.set_connections()

    def set_connections(self):
        self.window.connect_exportRaw(self.save_raw)
        self.window.connect_exportProcessed(self.save_processed)
        self.window.connect_showBatch(self.batch.show)
        self.window.connect_openFile(self.file_open)
        self.window.connect_selectFitting(self.fittings.load_current_fitting)
        self.window.connect_changeBasicSettings(self.redraw)


    def redraw(self):
        file = self.window.toutFilename.text()
        self.apply_data(file)

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
            if url.isValid() and url.scheme() in self.IMPORT["VALID_SCHEME"]:
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
        # TODO: Why check specific False? Why not falsy?
        if files is False:
            files = uni.load_files(self.lastdir);
            if len(files) > 1:
                self.batch.show();
                self.batch.update_filelist(files)
            elif len(files) == 1:
                files = files[0];
            else:
                files = "";


        if files != "":
            #str() for typecast from utf16(Qstring) to utf8(python string)
            self.lastdir = str(QFileInfo(files).absolutePath())

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
                        int(self.window.ddGrating.currentText()),
                        fittings=self.fittings,
                        funConnection=self.window.ConnectSlotResults)
        #calculate results
        # TODO: no validation of results?
        procX, procY = spec_proc.get_processed_data()
        baseline, avg = spec_proc.get_baseline()
        peak_height, peak_area = spec_proc.get_peak()

        # Clear the widget from previous spectra
        # Draw the spectra in MatPlotLibWidgets
        # Raw
        rawPlot = self.window.mplRaw;
        self.init_plot(rawPlot, self.PLOT["RAW_X_LABEL"], self.PLOT["RAW_Y_LABEL"]);
        self.update_plot(rawPlot, x_data, y_data,
                         self.PLOT["RAW_DATA_MRK"], self.PLOT["RAW_DATA_LABEL"]);
        self.update_plot(rawPlot, x_data, baseline,
                         self.PLOT["RAW_BASELINE_MRK"], self.PLOT["RAW_BASELINE_LABEL"]);

        # Processed
        processedPlot = self.window.mplProcessed;
        self.init_plot(processedPlot, self.PLOT["PROCESSED_X_LABEL"], self.PLOT["PROCESSED_Y_LABEL"]);
        self.update_plot(processedPlot, procX, procY,
                         self.PLOT["PROCESSED_DATA_MRK"], self.PLOT["PROCESSED_DATA_LABEL"]);


        # Enable Redraw Events
        # TODO: obsolet?
        self.plot_redrawable(True)

        return 0

    def save_raw(self, filename):
        """Save Raw-Data in CSV-File """
        print("Export Raw spectrum")
        # collect data
        filename, timestamp = self.get_fileinformation()
        labels = [self.PLOT["RAW_X_LABEL"], self.PLOT["RAW_Y_LABEL"]]
        xyData = uni.extract_xy_data(self.window.mplRaw.axes,
                                     self.PLOT["RAW_DATA_LABEL"])
        # write data to csv
        csvWriter = FileWriter(self, filename, timestamp)
        isExported = csvWriter.write_data(xyData, labels, ExportType.RAW)
        if isExported == 0:
            dialog.information_ExportFinished(filename)
        return 0;

    def save_processed(self, filename):
        """Save processed spectrum to CSV-File """
        # collect data
        filename, timestamp = self.get_fileinformation()
        labels = [self.PLOT["PROCESSED_X_LABEL"], self.PLOT["PROCESSED_Y_LABEL"]]
        xyData = uni.extract_xy_data(self.window.mplProcessed.axes,
                                     self.PLOT["PROCESSED_DATA_LABEL"])

        results = {}
        # TODO: use enum?
        results["Peak Height"] = self.window.toutPeakHeight.text()
        results["Peak Area"] = self.window.toutPeakArea.text()

        # write data to csv
        csvWriter = FileWriter(self, filename, timestamp)
        isExported = csvWriter.write_data(xyData, labels, ExportType.PROCESSED, results)
        if isExported == 0:
            dialog.information_ExportFinished(filename)
        return 0;

    def init_plot(self, plotObj, xlabel, ylabel):
        # TODO: errorhandling
        """Gets a plot object and label it after clearing it"""
        plotObj.axes.clear();
        plotObj.axes.set_xlabel(xlabel);
        plotObj.axes.set_ylabel(ylabel);
        plotObj.axes.axhline(linewidth=self.PLOT["DEF_LINEWIDTH"],
                             color=self.PLOT["DEF_AXIS_COLOR"]);
        plotObj.axes.axvline(linewidth=self.PLOT["DEF_LINEWIDTH"],
                             color=self.PLOT["DEF_AXIS_COLOR"]);
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
        # self.window.actRedraw.setEnabled(enable);
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
