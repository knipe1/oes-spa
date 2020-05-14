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


    ## qt-signals
    # fileinformation
    SIG_filename = pyqtSignal(str)
    SIG_date = pyqtSignal(str)
    SIG_time= pyqtSignal(str)

    ### Properties

    @property
    def currentFile(self):
        """currentFile getter"""
        return self._currentFile

    @currentFile.setter
    def currentFile(self, file:FileReader):
        """currentFile setter: Updating the ui"""
        self._currentFile = file
        self.set_fileinformation(file)

    ### Methods

    def __init__(self, initialShow=True):
        """initialize the parent class ( == QMainWindow.__init__(self)"""
        super(AnalysisWindow, self).__init__()

        # Set file and directory
        self.lastdir = self.FILE["DEF_DIR"];
        self._currentFile = None;
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
        # self.fittings = Fitting(self.window.fittings)

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
        win.connect_select_fitting(self.update_results)
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

        try:
            for spectrum in spectra:
                spectrum.init_plot();
                spectrum.update_plot();
        except:
            self.logger.error("Could not draw spectra. Missing valid spectra.")

        return 0


    def update_results(self):
        """Updates the result section of the ui with the current file."""
        try:
            self.apply_data(self.currentFile.filename, updateSpectra=False)
        except AttributeError as err:
            self.logger.error("Currently no file selected to update results.")
            self.logger.error(err)


    def redraw(self, text:str=""):
        """
        Redraw the plots with the currently opened file.

        Uses self.currentFile.filename to get the filename.

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
            self.apply_data(self.currentFile.filename)
            self.logger.info("Redraw triggered by:" + text)
        except:
            self.logger.warning("Redraw Failed")


    ### fileinformation

    def get_fileinformation(self):
        # TODO: @property?
        # TODO: self.filename
        # TODO: self.filename = {name: asd, timestamp: sad}
        try:
            filename = self.currentFile.filename
            timestamp = self.currentFile.timestamp
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

    def apply_data(self, filename, updateSpectra=True, updateResults=True):
        """read out a file and extract its information,
        then set header information and draw spectra"""
        # TODO: error handling

        connect = self.window.connect_results if updateResults else None;

        # Prepare file.
        file = FileReader(filename)

        # Update plots and ui.
        basicSetting = self.window.get_basic_setting()
        specHandler = DataHandler(basicSetting,
                                  funConnection=connect)
        # Validate results?
        results = specHandler.analyse_data(file)

        if results is None:
            return -1

        # Update and the spectra.
        if updateSpectra:
            self.rawSpectrum.update_data(*specHandler.data)
            self.rawSpectrum.add_baseline(specHandler.baseline)
            self.processedSpectrum.update_data(*specHandler.procData)

            self.draw_spectra(self.rawSpectrum, self.processedSpectrum)

        # Update the currently open file.
        self.currentFile = file;
        return 0
