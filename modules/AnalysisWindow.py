#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


    Glossary:
        - activeFile: The file that is "active" (plotted and the results shown are analyzed from this file.)
@author: Hauke Wernecke
"""

# standard libs
from os import path

# third-party libs
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QMainWindow

# local modules/libs
from ui.UIMain import UIMain
from ConfigLoader import ConfigLoader
from Logger import Logger
import modules.Universal as uni
import dialog_messages as dialog
from modules.BatchAnalysis import BatchAnalysis
from modules.DataHandler import DataHandler
from modules.FileReader import FileReader
from modules.Spectrum import Spectrum
from modules.SpectrumWriter import SpectrumWriter

# enums
from custom_types.BasicSetting import BasicSetting
from custom_types.EXPORT_TYPE import EXPORT_TYPE

# constants


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

    ### Properties

    @property
    def activeFile(self)->FileReader:
        """activeFile getter"""
        return self._activeFile

    @activeFile.setter
    def activeFile(self, file:FileReader)->None:
        """activeFile setter: Updating the ui"""

        isFileReloaded = (self._activeFile == file)
        self._activeFile = file
        self.set_fileinformation(file)

        # Set additional information (like from asc-file). Or clear previous information.
        self.window.update_information(file.parameter)

        # Set Wavelength if provided and a freshly loaded file.
        if not isFileReloaded:
            self.set_wavelength_from_file(file)


    @property
    def lastdir(self):
        """Gets the directory which is preset for dialogs."""
        return self._lastdir

    @lastdir.setter
    def lastdir(self, directory:str):
        """Sets the directory which is preset for dialogs."""
        if path.isdir(directory):
            newDirectory = directory
        elif path.isfile(directory):
            newDirectory = path.dirname(directory)
        else:
            return

        self._lastdir = newDirectory


    ### __Methods__

    def __init__(self, initialShow=True):
        super().__init__()
        self.logger = Logger(__name__)


        # Set defaults.
        self.lastdir = self.FILE["DEF_DIR"];
        self._activeFile = None;

        ## Set up the user interfaces
        self.window = UIMain(self)
        self.batch = BatchAnalysis(self)

        self.__post_init__()

        # initial settings
        if initialShow:
            self.show()


    def __post_init__(self):
        self.init_connections()
        self.init_spectra()


    def __repr__(self):
        info = {}
        info["activeFile"] = self.activeFile
        info["lastdir"] = self.lastdir
        return self.__module__ + ":\n" + str(info)


    def init_spectra(self):
        """Set up the Spectrum elements with the corresponding ui elements."""
        self.rawSpectrum = Spectrum(self.window.plotRawSpectrum, EXPORT_TYPE.RAW)
        self.processedSpectrum = Spectrum(self.window.plotProcessedSpectrum, EXPORT_TYPE.PROCESSED);

    def init_connections(self):
        # TODO: docstring
        win = self.window
        win.connect_export_raw(self.export_raw)
        win.connect_export_processed(self.export_processed)
        win.connect_show_batch(self.batch.show)
        win.connect_open_file(self.file_open)
        win.connect_select_fitting(self.apply_fitting)
        win.connect_change_basic_settings(self.redraw)


    ### Events

    def closeEvent(self, event):
        """Closing the BatchAnalysis dialog to have a clear shutdown."""
        self.batch.schedule_cancel_routine()
        self.batch.close()


    def dragEnterEvent(self, event):
        """
        Drag Element over Window event.

        Handles only number of files:
            single file-> AnalysisWindow,
            multiple files-> BatchAnalysis.

        Validation takes place in dropEvent-handler.
        """


        # Handle the urls. Multiple urls are handled by BatchAnalysis.
        urls = event.mimeData().urls();
        isSingleFile = (len(urls) == 1)
        isMultipleFiles =(len(urls) > 1)

        if isMultipleFiles:
            self.batch.show();
        elif isSingleFile:
            event.accept()


    def dropEvent(self, event):
        """
        Drop File in window event.

        Validation and further processing of the data.

        event.accept --> dropEvent is handled by current Widget.
        """
        event.accept();

        # Can only be one single file.
        url = event.mimeData().urls()[0];
        localUrl = uni.get_valid_local_url(url)

        if localUrl:
            self.apply_data(localUrl)
        else:
            dialog.critical_unknownSuffix(parent=self)


    ### Methods


    def file_open(self):
        """Open FileDialog to select one or multiple spectra."""
        # File-->Open
        # Browse

        # Cancel/Quit dialog --> [].
        # One file selected: Update spectrum.
        # Multiple files: BatchAnalysis.
        filelist = dialog.dialog_openSpectra(self.lastdir);
        isSingleFile = (len(filelist) == 1)
        isMultipleFiles =(len(filelist) > 1)

        if isMultipleFiles:
            self.batch.show();
            self.batch.update_filelist(filelist)
        elif isSingleFile:
            filename = filelist[0];
            self.apply_data(filename)


    ### Export

    def export_spectrum(self, spectrum:Spectrum, results:dict={}):
        """Export raw/processed spectrum."""

        if not self.activeFile:
            # TODO: Put this into SpectrumWriter.export()?
            dialog.information_ExportAborted();
            return

        # Collect data.
        filename, timestamp = self.get_fileinformation()
        labels = spectrum.labels.values()
        xyData = spectrum.data.transpose()

        csvWriter = SpectrumWriter(filename, timestamp)
        csvWriter.export(xyData, labels, spectrum.exportType, results)


    def export_raw(self):
        """Export the raw spectrum."""
        self.export_spectrum(self.rawSpectrum)


    def export_processed(self):
        """Export the processed spectrum with the analyical characteristics."""
        results = self.window.get_results();
        self.export_spectrum(self.processedSpectrum, results)


    ### Draw Plots.

    def draw_spectra(self, *spectra):
        """Init and plot the given spectra."""
        for spectrum in spectra:
            spectrum.plot_spectrum()


    def apply_fitting(self):
        """
        Apply the fitting for the active file again.

        Prevent that the spectrum is again plotted.
        """
        try:
            self.apply_data(self.activeFile.filename, updateResults=True, updateSpectra=False)
        except AttributeError as err:
            self.logger.error("Could not apply the fitting.")
            self.logger.error(err)


    def redraw(self, value:str=None):
        """
        Redraw the plots with the currently opened file.

        Parameters
        ----------
        text : str
            The text of the new selected option. Informative in the logger.

        """
        try:
            self.apply_data(self.activeFile.filename)
            self.logger.info("New value of setting:" + value)
        except:
            self.logger.warning("Redraw Failed")


    ### fileinformation

    def get_fileinformation(self):
        # TODO: @property?
        # TODO: self.filename
        # TODO: self.filename = {name: asd, timestamp: sad}
        try:
            filename = self.activeFile.filename
            timestamp = self.activeFile.timestamp
        except:
            self.logger.error("Could not get filename/fileinformation.")
            filename = None;
            timestamp = None;

        return filename, timestamp


    def set_fileinformation(self, filereader:FileReader):
        """Updates the fileinformation"""
        filename, date, time = filereader.header
        self.window.set_fileinformation(filename, date, time)


    ### data analysis

    def apply_data(self, filename:str, updateSpectra=True, updateResults=True):
        """read out a file and extract its information,
        then set header information and draw spectra"""
        # TODO: error handling

        connect = self.window.connect_results if updateResults else None;

        # Prepare file.
        file = FileReader(filename)
        if not file.is_valid_spectrum():
            return

        basicSetting = self.window.get_basic_setting()

        self.show_wavelength_difference_information(file, basicSetting)

        specHandler = DataHandler(basicSetting, funConnection=connect, parameter=file.parameter)
        # Validate results?
        results = specHandler.analyse_data(file)

        if results is None:
            return

        # Update and the spectra.
        if updateSpectra:
            data = specHandler.data
            baseline = specHandler.baseline
            processedData = specHandler.procData

            rawIntegration, procIntegration = specHandler.get_integration_area()

            self.rawSpectrum.update_data(data, rawIntegration, baselineData=baseline)
            self.processedSpectrum.update_data(processedData, procIntegration)

            self.draw_spectra(self.rawSpectrum, self.processedSpectrum)

        # Update the currently open file.
        self.activeFile = file;


    def set_wavelength_from_file(self, file:FileReader):
        # TODO: docstring
        try:
            self.window.wavelength = file.WAVELENGTH
        except KeyError:
            # Exception if a non-.asc file is loaded.
            self.logger.debug("No Wavelength provided by: " + file.filename)


    def show_wavelength_difference_information(self, file:FileReader, basicSetting:BasicSetting):
        try:
            hasDifferentWl = (float(file.WAVELENGTH) != basicSetting.wavelength)
        except KeyError:
            hasDifferentWl = False
        finally:
            self.window.show_diff_wavelength(hasDifferentWl)