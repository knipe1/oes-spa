#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Hauke Wernecke
"""


# third-party libs
from PyQt5.QtCore import QFileInfo, pyqtSignal
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
from modules.Spectrum import Spectrum
from ui.UIMain import UIMain
from Logger import Logger



class AnalysisWindow(QMainWindow):
    """
    Main Window. Organization and interfaces of sub-types/windows.


    Further descriptions...

    Usage:
        TODO

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


    # set up the logger
    logger = Logger(__name__)


    # qt-signals
    signal_filename = pyqtSignal(str)
    signal_date = pyqtSignal(str)
    signal_time= pyqtSignal(str)

    def __init__(self, initialShow=True):
        """initialize the parent class ( == QMainWindow.__init__(self)"""
        super(AnalysisWindow, self).__init__()

        # Set file and directory
        self.lastdir = self.FILE["DEF_DIR"];
        self.openFile = None;
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
        # TODO: provide interface? Like get_fittings? No, it is a attribute
        # using the @property-decorator --> to be documented?
        self.fittings = Fitting(self.window.fittings)

        self.__post_init__()

        # initial settings
        if initialShow:
            self.show()

    def __post_init__(self):
        self.set_connections()
        self.init_spectra()

    def set_connections(self):
        win = self.window
        win.connect_export_raw(self.export_raw)
        win.connect_export_processed(self.export_processed)
        win.connect_show_batch(self.batch.show)
        win.connect_open_file(self.file_open)
        win.connect_select_fitting(self.fittings.load_current_fitting)
        win.connect_change_basic_settings(self.redraw)

    def init_spectra(self):
        self.rawSpectrum = Spectrum(self.window.get_raw_plot(), ExportType.RAW)
        self.processedSpectrum = Spectrum(self.window.get_processed_plot(),
                                          ExportType.PROCESSED);

    def closeEvent(self, event):
        """Closing the BatchAnalysis dialog to have a clear shutdown."""
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
        if not len(x_data) and len(x_data) == len(y_data):
            dialog.critical_unknownFiletype(self)
            return 1

        # Sent the raw data to the DataHandler and get parameters
        # TODO: function required for getting parameters and errorhandling!
        # TODO: Is Central wavelength depending on the selected Fitting?
        spec_proc = DataHandler(x_data, y_data,
                        self.window.get_central_wavelength(),
                        self.window.get_grating(),
                        fittings=self.fittings,
                        funConnection=self.window.connect_results)
        #calculate results
        # TODO: no validation of results?
        procX, procY = spec_proc.get_processed_data()
        baseline, avg = spec_proc.get_baseline()
        peak_height, peak_area = spec_proc.get_peak()

        # Draw the spectra in MatPlotLibWidgets
        # Raw
        # config
        self.rawSpectrum.update_data(x_data, y_data)
        self.rawSpectrum.add_baseline(baseline)

        # plotting
        # self.init_plot(rawSpectrum.ui, **rawSpectrum.labels);
        self.init_plot(self.rawSpectrum);
        self.update_plot(self.rawSpectrum)
        # self.update_plot(rawSpectrum.ui, rawSpectrum.xData, rawSpectrum.yData,
        #                  **rawSpectrum.markup);
        # self.update_plot(rawSpectrum.ui, x_data, rawSpectrum.baseline,
        #                  **rawSpectrum.baselineMarkup);

        # Processed
        # config

        self.processedSpectrum.update_data(procX, procY)
        # self.processedSpectrum.add_baseline(baseline)
        # processedSpectrum = Spectrum(self.window.mplProcessed, procX, procY,
        #                              ExportType.PROCESSED)
        # plotting
        # self.init_plot(processedSpectrum.ui, **processedSpectrum.labels);
        self.init_plot(self.processedSpectrum);
        self.update_plot(self.processedSpectrum);
        # self.update_plot(processedSpectrum.ui, processedSpectrum.xData,
        #                  processedSpectrum.yData, **processedSpectrum.markup);


        # Enable Redraw Events
        # TODO: obsolet?
        # self.plot_redrawable(True)

        return 0

    def export_spectrum(self, spectrum):
        """Export raw/processed spectrum."""
        isExported = True

        # collect data
        filename, timestamp = self.get_fileinformation()
        labels = spectrum.labels
        xyData = uni.extract_xy_data(spectrum.ui.axes,
                                     spectrum.markup.get("label"))

        if filename == None:
            isExported = False;

        if xyData is None:
            isExported = False;

        if isExported:
            # write data to csv
            csvWriter = FileWriter(self, filename, timestamp)
            isExported = csvWriter.write_data(xyData, labels,
                                              spectrum.exportType)

        if not isExported:
            dialog.information_ExportAborted();

        return isExported;

    def export_raw(self):
        """Save Raw-Data in CSV-File """
        self.export_spectrum(self.rawSpectrum)
        return 0
        # # collect data
        # filename, timestamp = self.get_fileinformation()
        # if filename == None:
        #     return 1
        # labels = [self.PLOT["RAW_X_LABEL"], self.PLOT["RAW_Y_LABEL"]]
        # xyData = uni.extract_xy_data(self.window.mplRaw.axes,
        #                              self.PLOT["RAW_DATA_LABEL"])
        # # write data to csv
        # csvWriter = FileWriter(self, filename, timestamp)
        # isExported = csvWriter.write_data(xyData, labels, ExportType.RAW)
        # if isExported:
        #     dialog.information_ExportFinished(filename)
        # return 0;

    def export_processed(self, filename):
        """Save processed spectrum to CSV-File """
        # implement Peak Height and Peak Area
        self.export_spectrum(self.processedSpectrum)
        return 0
        # # collect data
        # filename, timestamp = self.get_fileinformation()
        # labels = [self.PLOT["PROCESSED_X_LABEL"], self.PLOT["PROCESSED_Y_LABEL"]]
        # xyData = uni.extract_xy_data(self.window.mplProcessed.axes,
        #                              self.PLOT["PROCESSED_DATA_LABEL"])

        # results = {}
        # # TODO: use enum?
        # results["Peak Height"] = self.window.toutPeakHeight.text()
        # results["Peak Area"] = self.window.toutPeakArea.text()

        # # write data to csv
        # csvWriter = FileWriter(self, filename, timestamp)
        # isExported = csvWriter.write_data(xyData, labels, ExportType.PROCESSED, results)
        # if isExported:
        #     dialog.information_ExportFinished(filename)
        # return 0;

    # def init_plot(self, plotObj, xLabel, yLabel):
    #     # TODO: errorhandling
    #     """Gets a plot object and label it after clearing it"""
    #     plotObj.axes.clear();
    #     plotObj.axes.set_xlabel(xLabel);
    #     plotObj.axes.set_ylabel(yLabel);
    #     plotObj.axes.axhline(linewidth=self.PLOT["DEF_LINEWIDTH"],
    #                          color=self.PLOT["DEF_AXIS_COLOR"]);
    #     plotObj.axes.axvline(linewidth=self.PLOT["DEF_LINEWIDTH"],
    #                          color=self.PLOT["DEF_AXIS_COLOR"]);
    #     return 0;

    def init_plot(self, spectrum):
        # TODO: compare dict["key"] -> error if not found
        # vs dict.get("key") -> default styles if not found
        # vs config of rcParams in init -> overview and default styles if not
        # found and central configuration
        lineMarkup = {"linewidth": self.PLOT.get("DEF_LINEWIDTH"),
                      "color": self.PLOT.get("DEF_AXIS_COLOR")}

        axes = spectrum.ui.axes
        axes.clear();
        axes.set_xlabel(spectrum.labels.get("xLabel"));
        axes.set_ylabel(spectrum.labels.get("yLabel"));
        axes.axhline(**lineMarkup)
        axes.axvline(**lineMarkup)


    # def update_plot(self, plotObj, xData, yData, color, label):
    #     """updates a given plot"""
    #     # TODO: errorhandling
    #     plotObj.axes.plot(xData, yData, color, label=label);
    #     plotObj.axes.set_xlim(xData[0], xData[-1]);
    #     plotObj.axes.legend();
    #     plotObj.draw();
    #     return 0;


    def update_plot(self, spectrum):
        """updates a given plot"""
        # TODO: errorhandling
        # define variables for easier maintenance
        axes = spectrum.ui.axes
        spec = spectrum

        # plotting
        axes.plot(spec.xData, spec.yData, **spec.markup);
        if len(spec.baseline):
            axes.plot(spec.xData, spec.baseline, **spec.baselineMarkup);

        # zoom to specific area
        axes.set_xlim(spec.xData[0], spec.xData[-1]);
        axes.legend();

        spec.ui.draw();
        return 0;


    # def plot_redrawable(self, enable = True):
    #     """set the status (enabled/disabled) of redraw button/action"""
    #     # self.window.actRedraw.setEnabled(enable);
    #     # menu --> File --> save
    #     # TODO: but important!!!
    #     self.window.menuSave.setEnabled(enable)
    #     return 0;

    def get_fileinformation(self):
        # TODO: self.filename
        # TODO: self.timestamp
        # TODO: self.filename = {name: asd, timestamp: sad}
        try:
            filename = self.openFile.filename
            date = self.openFile.date
            time = self.openFile.time
            timestamp = date + " " + time
        except:
            self.logger.error("Could not get filename/fileinformation.")
            filename = None;
            timestamp = None;

        return filename, timestamp

    def set_fileinformation(self, filereader:FileReader):
        """Updates the fileinformation"""
        # TODO: date+time = timestamp?
        # TODO: validate inputs
        # TODO: try catch?
        # TODO: Review. Pythonic? Clean distinction between UI and logic, but
        # looks kind of unstructured...
        try:
            time, date = filereader.get_head()

            # set values
            self.window.connect_fileinformation(self.signal_filename,
                                                self.signal_date,
                                                self.signal_time)
            self.signal_filename.emit(filereader.filename)
            self.signal_date.emit(date)
            self.signal_time.emit(time)
        except:
            pass

    def apply_data(self, filename):
        """read out a file and extract its information,
        then set header information and draw spectra"""
        # TODO: error handling
        # Read out the chosen file
        self.openFile = FileReader(filename)
        np_x, np_y = self.openFile.get_values()

        # Validation.
        if not (np_x.size and np_y.size):
            return 1
        # Update plots and ui.
        self.draw_spectra(np_x, np_y)
        self.set_fileinformation(self.openFile)
        return 0


    def redraw(self, text:str=""):
        """
        Redraw the plots with the currently opened file.

        Uses self.openFile.filename to get the filename.

        Parameters
        ----------
        text : str
            The text of the new selected option. Informative in the logger.
            (Default: "")

        Returns
        -------
        None.

        """
        try:
            self.apply_data(self.openFile.filename)
            self.logger.info("Redraw triggered by:" + text)
        except:
            pass

