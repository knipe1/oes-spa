#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Hauke Wernecke
"""


# third-party libs
from PyQt5.QtCore import QFileInfo, pyqtSignal
from PyQt5.QtWidgets import QMainWindow

# local modules/libs
from ConfigLoader import ConfigLoader
import modules.Universal as uni
import dialog_messages as dialog
from modules.BatchAnalysis import BatchAnalysis
from modules.DataHandler import DataHandler
from modules.FileReader import FileReader
from modules.FileWriter import FileWriter
from modules.Fitting import Fitting
from modules.Spectrum import Spectrum
from ui.UIMain import UIMain
from Logger import Logger

# enums
from custom_types.CHARACTERISTIC import CHARACTERISTIC
from custom_types.EXPORT_TYPE import EXPORT_TYPE


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

    # Load the configuration for plotting, import and filesystem properties.
    config = ConfigLoader()
    PLOT = config.PLOT;
    FILE = config.FILE
    IMPORT = config.IMPORT

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

    def init_spectra(self):
        self.rawSpectrum = Spectrum(self.window.get_raw_plot(),
                                    EXPORT_TYPE.RAW)
        self.processedSpectrum = Spectrum(self.window.get_processed_plot(),
                                          EXPORT_TYPE.PROCESSED);

    def set_connections(self):
        win = self.window
        win.connect_export_raw(self.export_raw)
        win.connect_export_processed(self.export_processed)
        win.connect_show_batch(self.batch.show)
        win.connect_open_file(self.file_open)
        win.connect_select_fitting(self.fittings.load_current_fitting)
        win.connect_change_basic_settings(self.redraw)
        win.connect_fileinformation(self.SIG_filename, self.SIG_date,
                                    self.SIG_time)


    ### Events

    def closeEvent(self, event):
        """Closing the BatchAnalysis dialog to have a clear shutdown."""
        self.batch.close()


    def dragEnterEvent(self, event):
        """
        Drag Element over Window event.

        Handles only number of files: One file->AnalysisWindow, more files->
        BatchAnalysis. Validation takes place in dropEvent-handler.
        """

        # Prequerities.
        urls = event.mimeData().urls();

        # Handle the urls. Multiple urls are handled by BatchAnalysis.
        if len(urls) > 1:
            self.batch.show();
        elif len(urls) == 1:
            event.accept()


    def dropEvent(self, event):
        """
        Drop File in window event.

        Validation and further processing of the data.

        event.accept --> dropEvent is handled by current Widget.
        """
		# TODO: errorhandling?
        # Can only be one single file. Otherwise would be rejected by
        # dragEvent-handler.
        url = event.mimeData().urls()[0];
        localUrl = url.toLocalFile();

        # Validation.
        if uni.is_valid_filetype(url):
            event.accept();
            self.apply_data(localUrl)
        else:
            dialog.critical_unknownSuffix(parent=self)


    ### Methods

    def file_open(self, filename):
        """Open FileDialog to choose Raw-Data-File """
        # Load a file via menu bar
        # File-->Open
        # Batch-->Drag&Drop or -->Browse Files
        # TODO: doublecheck batch handling here. Look up event management
        # TODO: Why check specific False? Why not falsy?

        # filename is False, when an event of actOpen in the menu bar
        # (File-->Open) is triggered.
        # TODO: is False or == False or filename:?
        # if filename is False:
        if not filename:
            # Cancel/Quit dialog --> [].
            # One file selected: Update spectra.
            # Multiple files: BatchAnalysis.
            filename = dialog.dialog_openFiles(self.lastdir);
            if len(filename) > 1:
                self.batch.show();
                self.batch.update_filelist(filename)
            elif len(filename) == 1:
                filename = filename[0];
            else:
                filename = "";

        # Handling if just one file was selected or filename was given.
        if filename != "":
            self.lastdir = QFileInfo(filename).absolutePath()
            self.apply_data(filename)


    ### Export

    def export_spectrum(self, spectrum, results:dict={}):
        """Export raw/processed spectrum."""

        # Prequerities.
        spec = spectrum
        isExported = True

        # Collect data.
        filename, timestamp = self.get_fileinformation()
        labels = spec.labels.values()
        xyData = zip(spec.xData, spec.yData)
        # xyData = uni.extract_xy_data(spec.ui.axes,
        #                              spec.markup.get("label"))

        if filename == None:
            isExported = False;

        if xyData is None:
            isExported = False;

        if isExported:
            # write data to csv
            csvWriter = FileWriter(filename, timestamp)
            isExported = csvWriter.write_data(xyData, labels,
                                              spec.exportType, results)

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


    ### Draw Plots.

    def draw_spectra(self, *spectra):
        """Init and plot the given spectra."""

        for spectrum in spectra:
            if isinstance(spectrum, Spectrum):
                self.init_plot(spectrum);
                self.update_plot(spectrum);
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
        """Updates the ui using the element and data of the given spectrum."""
        # TODO: errorhandling
        spec = spectrum
        axes = spectrum.ui.axes

        # Plot the data and eventually a baseline.
        axes.plot(spec.xData, spec.yData, **spec.markup);
        if len(spec.baseline):
            axes.plot(spec.xData, spec.baseline, **spec.baselineMarkup);

        # Zoom to specific area.
        axes.update_layout(xLimit=(spec.xData[0], spec.xData[-1]));

        spec.ui.draw();
        return 0;


    def redraw(self, text:str=""):
        """
        Redraw the plots with the currently opened file.

        Uses self.openFile.filename to get the filename.

        Parameters
        ----------
        text : str
            The text of the new selected option. Informative in the logger.
            The default is "".

        Returns
        -------
        None.

        """
        try:
            self.apply_data(self.openFile.filename)
            self.logger.info("Redraw triggered by:" + text)
        except:
            self.logger.warning("Redraw Failed")


    ### fileinformation

    def get_fileinformation(self):
        # TODO: @property?
        # TODO: self.filename
        # TODO: self.filename = {name: asd, timestamp: sad}
        try:
            filename = self.openFile.filename
            timestamp = self.openFile.timestamp
        except:
            self.logger.error("Could not get filename/fileinformation.")
            filename = None;
            timestamp = None;

        return filename, timestamp


    def set_fileinformation(self, filereader:FileReader):
        """Updates the fileinformation"""
        # TODO: date+time = timestamp?
        # TODO: validate inputs
        # TODO: Review. Pythonic? Clean distinction between UI and logic, but
        # looks kind of unstructured...
        filename, date, time = filereader.header

        # Emit signals.
        self.SIG_filename.emit(filename)
        self.SIG_date.emit(date)
        self.SIG_time.emit(time)

    ### data analysis

    def apply_data(self, filename):
        """read out a file and extract its information,
        then set header information and draw spectra"""
        # TODO: error handling
        # Read out the chosen file
        file = FileReader(filename)

        # Validation.
        if not file.is_valid_datafile():
            dialog.critical_unknownFiletype(self)
            return 1

        # TODO: Why not as tuples? just data = [(x0, y0),(x1, y1),...]
        xData, yData = file.data

        # Update plots and ui.
        self.analyze_data(xData, yData)
        self.draw_spectra(self.rawSpectrum, self.processedSpectrum)
        self.set_fileinformation(file)

        # update the currently open file.
        # TODO: Check openFile as property --> setter method could contain
        # the update ui function?
        self.openFile = file;
        return 0

    def analyze_data(self, xData, yData, updateResults=True):
        """Analyze data with DataHandler to obtain all parameters for the
        processed spectrum.
        """

        connect = self.window.connect_results if updateResults else None;

        # Sent the raw data to the DataHandler and get parameters
        # TODO: function required for getting parameters and errorhandling!
        # TODO: Is Central wavelength depending on the selected Fitting?
        specHandler = DataHandler(xData, yData,
                        self.window.get_central_wavelength(),
                        self.window.get_grating(),
                        fittings=self.fittings,
                        funConnection=connect)

        #calculate results
        # TODO: no validation of results?
        procX, procY = specHandler.get_processed_data()
        baseline, avg = specHandler.get_baseline()
        peakHeight, peakArea = specHandler.get_peak()
        peakRawHeight, peakPosition = specHandler.get_raw_peak()

        # HACK ------------------------------------------------------
        # characteristics = {};
        # characteristics[CHARACTERISTIC.PEAK_AREA] = peakArea
        # HACK ------------------------------------------------------

        # Update and the spectra.
        self.rawSpectrum.update_data(xData, yData)
        self.rawSpectrum.add_baseline(baseline)
        self.processedSpectrum.update_data(procX, procY)

        # TODO: return dict with characteristics? return @dataclass?
        return 0




