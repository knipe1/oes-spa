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

# enums
from custom_types.CHARACTERISTIC import CHARACTERISTIC


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
    SIG_filename = pyqtSignal(str)
    SIG_date = pyqtSignal(str)
    SIG_time= pyqtSignal(str)

    def __init__(self, initialShow=True):
        """initialize the parent class ( == QMainWindow.__init__(self)"""
        super(AnalysisWindow, self).__init__()

        # Set file and directory
        self.lastdir = self.FILE["DEF_DIR"];
        self.openFile = None;
        # general settings
        # TODO: maybe false, if BatchAnalysis is open?
        self.setAcceptDrops(True)

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


    def draw_spectra(self, *spectra):
        """Init and plot the given spectra."""

        for spectrum in spectra:
            if isinstance(spectrum, Spectrum):
                self.init_plot(spectrum);
                self.update_plot(spectrum);
        return 0


    def export_spectrum(self, spectrum, results:dict={}):
        """Export raw/processed spectrum."""
        isExported = True

        # collect data
        filename, timestamp = self.get_fileinformation()
        labels = spectrum.labels.values()
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
                                              spectrum.exportType, results)

        if not isExported:
            dialog.information_ExportAborted();

        return isExported;

    def export_raw(self):
        """Save Raw-Data in CSV-File """

        self.export_spectrum(self.rawSpectrum)
        return 0

    def export_processed(self):
        """Save processed spectrum to CSV-File """

        results = self.window.get_results();
        self.export_spectrum(self.processedSpectrum, results)
        return 0


    def init_plot(self, spectrum):

        axes = spectrum.ui.axes
        labels = spectrum.labels

        # Reset plot.
        axes.clear();
        # Add a coordinate origin with default markup.
        axes.axhline()
        axes.axvline()
        # Update the labels of the plot.
        axes.update_layout(**labels)


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
        axes.update_layout(xLimit=(spec.xData[0], spec.xData[-1]));

        spec.ui.draw();
        return 0;


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
            self.window.connect_fileinformation(self.SIG_filename,
                                                self.SIG_date,
                                                self.SIG_time)
            self.SIG_filename.emit(filereader.filename)
            self.SIG_date.emit(date)
            self.SIG_time.emit(time)
        except:
            pass

    def apply_data(self, filename):
        """read out a file and extract its information,
        then set header information and draw spectra"""
        # TODO: error handling
        # Read out the chosen file
        file = FileReader(filename)
        xData, yData = file.get_values()

        # Update plots and ui.
        self.analyze_data(xData, yData)
        self.draw_spectra(self.rawSpectrum, self.processedSpectrum)
        self.set_fileinformation(file)

        self.openFile = file;
        return 0

    def analyze_data(self, xData, yData, updateResults=True):
        """Analyze data with DataHandler to obtain all parameters for the
        processed spectrum.
        """

        # Check for a valid structure of the data
        if not len(xData) and len(xData) == len(yData):
            dialog.critical_unknownFiletype(self)
            return 1

        connect = self.window.connect_results if updateResults else None;

        # Sent the raw data to the DataHandler and get parameters
        # TODO: function required for getting parameters and errorhandling!
        # TODO: Is Central wavelength depending on the selected Fitting?
        spec_proc = DataHandler(xData, yData,
                        self.window.get_central_wavelength(),
                        self.window.get_grating(),
                        fittings=self.fittings,
                        funConnection=connect)

        #calculate results
        # TODO: no validation of results?
        procX, procY = spec_proc.get_processed_data()
        baseline, avg = spec_proc.get_baseline()
        peak_height, peak_area = spec_proc.get_peak()
        peak_raw_height, peak_position = spec_proc.get_peak_raw()

        characteristics = {};
        characteristics[CHARACTERISTIC.PEAK_AREA] = peak_area

        # Update and plot the spectra
        self.rawSpectrum.update_data(xData, yData)
        self.rawSpectrum.add_baseline(baseline)
        self.processedSpectrum.update_data(procX, procY)

        # TODO: return dict with characteristics?
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
            self.logger.warning("Redraw Failed")

