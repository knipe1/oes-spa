#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


    Glossary:
        - currentFile: The file that is "active" (plotted and the results shown are analyzed from this file.)
@author: Hauke Wernecke
"""

# standard libs
from os import path

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
from modules.SpectrumWriter import SpectrumWriter
from modules.Spectrum import Spectrum
from ui.UIMain import UIMain
from Logger import Logger

# enums
from custom_types.ASC_PARAMETER import ASC_PARAMETER as ASC
from custom_types.EXPORT_TYPE import EXPORT_TYPE


class AnalysisWindow(QMainWindow):
    """
    Main Window. Organization and interfaces of sub-types/sub-windows.

    Usage:
        from modules.AnalysisWindow import AnalysisWindow
        window = AnalysisWindow()
        window.apply_data("./sample files/Asterix1059 1.Spk") # Load a spectrum programmatically.
    """

    # Load the configuration for plotting, import and filesystem properties.
    config = ConfigLoader()
    PLOT = config.PLOT;
    FILE = config.FILE
    IMPORT = config.IMPORT

    ## qt-signals
    # fileinformation
    SIG_filename = pyqtSignal(str)
    SIG_date = pyqtSignal(str)
    SIG_time= pyqtSignal(str)

    ### Properties

    @property
    def currentFile(self)->FileReader:
        """currentFile getter"""
        return self._currentFile

    @currentFile.setter
    def currentFile(self, file:FileReader):
        """currentFile setter: Updating the ui"""

        isFileReloaded = (self._currentFile == file)
        self._currentFile = file
        self.set_fileinformation(file)

        # Set additional information (like from asc-file).
        # Or clear previous information.
        self.window.update_information(file.parameter)

        # Set Wavelength if provided and a freshly loaded file.
        if not isFileReloaded:
            self.set_wavelength_from_file(file)


    @property
    def lastdir(self):
        """lastdir getter"""
        return self._lastdir

    @lastdir.setter
    def lastdir(self, directory:str):
        """lastdir setter: Updating the parent"""
        if path.isdir(directory):
            newDirectory = directory
        elif path.isfile(directory):
            newDirectory = path.dirname(directory)
        else:
            return

        self._lastdir = newDirectory


    ### __Methods__

    def __init__(self, initialShow=True):
        # TODO: docstring?

        self.logger = Logger(__name__)

        #initialize the parent class ( == QMainWindow.__init__(self)
        super(AnalysisWindow, self).__init__()

        # Set defaults.
        # TODO: new method? Issue with inheritance.
        self.lastdir = self.FILE["DEF_DIR"];
        self._currentFile = None;

        ## Set up the user interfaces (main application window, batch window)
        self.window = UIMain(self)
        self.batch = BatchAnalysis(self)

        self.__post_init__()

        # initial settings
        if initialShow:
            self.show()

    def __post_init__(self):
        self.set_connections()
        self.init_spectra()


    def __repr__(self):
        info = {}
        info["currentFile"] = self.currentFile
        info["lastdir"] = self.lastdir
        return self.__module__ + ":\n" + str(info)


    def init_spectra(self):
        # TODO: docstring
        self.rawSpectrum = Spectrum(self.window.get_raw_plot(), EXPORT_TYPE.RAW)
        self.processedSpectrum = Spectrum(self.window.get_processed_plot(), EXPORT_TYPE.PROCESSED);

    def set_connections(self):
        # TODO: docstring
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

        Handles only number of files:
            1 file-> AnalysisWindow,
            more files-> BatchAnalysis.

        Validation takes place in dropEvent-handler.
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

        # Can only be one single file. Otherwise would be rejected by
        # dragEvent-handler.
        url = event.mimeData().urls()[0];

        # Validation.
        localUrl = uni.get_valid_local_url(url)
        if localUrl:
            self.apply_data(localUrl)
            event.accept();
        else:
            dialog.critical_unknownSuffix(parent=self)


    ### Methods


    def set_wavelength_from_file(self, file:FileReader):
        # TODO: docstring
        try:
            self.window.wavelength = file.WAVELENGTH
        except KeyError:
            # Exception if a non-.asc file is loaded.
            self.logger.debug("No Wavelength provided by: " + file.filename)


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
            fileInfo = QFileInfo(filename)
            self.lastdir = fileInfo.absolutePath()
            filename = fileInfo.absoluteFilePath()
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
        xyData = spec.data.transpose()

        if filename == None:
            isExported = False;

        if xyData is None:
            isExported = False;

        if isExported:
            csvWriter = SpectrumWriter(filename, timestamp)
            csvWriter.export(xyData, labels, spec.exportType, results)
        else:
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
                spectrum.plot_spectrum()
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
        if not file.is_valid_spectrum():
            return

        # Update plots and ui.
        basicSetting = self.window.get_basic_setting()

        # Check for differences in entered WL and stored WL
        try:
            showDiffWL = (float(file.WAVELENGTH) != basicSetting.wavelength)
        except KeyError:
            showDiffWL = False
        finally:
            self.window.show_diff_wavelength(showDiffWL)


        specHandler = DataHandler(basicSetting, funConnection=connect, parameter=file.parameter)
        # Validate results?
        results = specHandler.analyse_data(file)

        if results is None:
            return -1

        # Update and the spectra.
        if updateSpectra:
            data = specHandler.data
            baseline = specHandler.baseline
            processedData = specHandler.procData

            rawIntegration, procIntegration = self.get_integration_area(specHandler)

            self.rawSpectrum.update_data(data, rawIntegration, baselineData=baseline)
            self.processedSpectrum.update_data(processedData, procIntegration)

            self.draw_spectra(self.rawSpectrum, self.processedSpectrum)

        # Update the currently open file.
        self.currentFile = file;
        return 0

    ### unsorted
    def get_integration_area(self, dataHandler):
        rawIntegration = []
        procIntegration = []
        for intArea in dataHandler.integration:
            if intArea.spectrumType == EXPORT_TYPE.RAW:
                rawIntegration.append(intArea)
            else:
                procIntegration.append(intArea)

        return rawIntegration, procIntegration
