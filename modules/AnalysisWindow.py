#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Glossary:
        - activeFile: The file that is "active" (plotted and the results shown are analyzed from this file.)

@author: Hauke Wernecke
"""

# standard libs
from os import path, getcwd

# third-party libs
from PyQt5.QtWidgets import QMainWindow

# local modules/libs
from ui.UIMain import UIMain
from ConfigLoader import ConfigLoader
from Logger import Logger
import modules.Universal as uni
import dialog_messages as dialog
from modules.BatchAnalysis import BatchAnalysis
from modules.dataanalysis.SpectrumHandler import SpectrumHandler
from modules.filehandling.filereading.FileReader import FileReader
from modules.dataanalysis.Spectrum import Spectrum
from modules.filehandling.filewriting.SpectrumWriter import SpectrumWriter

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
        window.apply_file("./sample files/Asterix1059 1.Spk") # Load a spectrum programmatically.
    """

    # Load the configuration for plotting, import and filesystem properties.
    config = ConfigLoader()
    PLOT = config.PLOT;
    GENERAL = config.GENERAL

    ### Properties

    @property
    def activeFile(self)->FileReader:
        """activeFile getter"""
        return self._activeFile

    @activeFile.setter
    def activeFile(self, file:FileReader)->None:
        """activeFile setter: Updating the ui"""
        self.window.set_fileinformation(file)

        # Set additional information (like from asc-file). Or clear previous information.
        self.window.update_information(file.parameter)

        self._activeFile = file


    @property
    def lastdir(self)->str:
        """Gets the directory which is preset for dialogs."""
        return self._lastdir

    @lastdir.setter
    def lastdir(self, directory:str):
        if path.isdir(directory):
            newDirectory = directory
        elif path.isfile(directory):
            newDirectory = path.dirname(directory)
        elif not hasattr(self, "lastdir"):
            newDirectory = getcwd()
        else:
            return

        self._lastdir = newDirectory


    ### __Methods__

    def __init__(self)->None:
        super().__init__()
        self.logger = Logger(__name__)

        # Set defaults.
        self.lastdir = self.GENERAL["INITIAL_DIR"];
        self._activeFile = None;

        ## Set up the user interfaces
        self.window = UIMain(self)
        self.batch = BatchAnalysis(self)

        self.__post_init__()

        # Show window, otherwise the window does not appear anywhere on the screen.
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
        win = self.window
        win.connect_export_raw(self.export_raw)
        win.connect_export_processed(self.export_processed)
        win.connect_show_batch(self.batch.show)
        win.connect_open_file(self.file_open)
        win.connect_change_basic_settings(self.redraw)


    ### Events

    def closeEvent(self, event):
        """Closing the BatchAnalysis dialog to have a clear shutdown."""
        self.batch.schedule_cancel_routine()
        self.batch.close()


    def dragEnterEvent(self, event):
        # Handle the urls. Multiple urls are handled by BatchAnalysis.
        urls = event.mimeData().urls();
        isSingleFile = (len(urls) == 1)
        isMultipleFiles =(len(urls) > 1)

        if isMultipleFiles:
            self.batch.show();
        elif isSingleFile:
            event.accept()


    def dropEvent(self, event):
        event.accept();

        # Can only be one single file.
        url = event.mimeData().urls()[0];
        localUrl = uni.get_valid_local_url(url)

        if localUrl:
            self.apply_file(localUrl)
        else:
            dialog.critical_unknownSuffix(parent=self)


    ### Methods

    def file_open(self):
        """Open FileDialog to select one or multiple spectra."""
        # File-->Open
        # Browse

        # Cancel/Quit dialog --> [].
        # filelist = dialog.dialog_spectra(self.lastdir);
        filelist = dialog.dialog_spectra();
        isSingleFile = (len(filelist) == 1)
        isMultipleFiles = (len(filelist) > 1)

        if isMultipleFiles:
            self.batch.show();
            self.batch.update_filelist(filelist)
        elif isSingleFile:
            filename = filelist[0];
            self.apply_file(filename)
        try:
            self.lastdir = filelist[0]
        except IndexError:
            pass


    ### Export

    def export_raw(self):
        self.export_spectrum(self.rawSpectrum)


    def export_processed(self):
        results = self.window.get_results();
        self.export_spectrum(self.processedSpectrum, results)


    def export_spectrum(self, spectrum:Spectrum, results:dict={}):

        try:
            writer = SpectrumWriter(*self.activeFile.fileinformation)
        except AttributeError:
            dialog.information_exportNoSpectrum()
            return

        exportedFilename = writer.export(spectrum, results)
        if exportedFilename:
            dialog.information_exportFinished(exportedFilename)
        else:
            dialog.information_exportAborted()


    def redraw(self, value:str=None):
        """
        Redraw the plots with the currently opened file.

        Parameters
        ----------
        value : str
            The text of the new selected option. Informative in the logger.

        """
        try:
            self.logger.info(f"New value of setting: {value}. Redraw of {self.activeFile.filename}.")
            self.apply_data(self.activeFile)
        except AttributeError:
            self.logger.warning("Redraw Failed")


    ### data analysis

    def apply_file(self, filename:(str, FileReader), silent:bool=False)->None:
        """read out a file and extract its information, then set header information and draw spectra"""
        try:
            file = FileReader(filename)
        except TypeError:
            file = filename

        if not silent:
            # Hint: set wavelength triggers a redraw loop. If wavelength is set after basicSetting is loaded, the analysis will not update the setting.
            isFileReloaded = (self.activeFile == file)
            if not isFileReloaded:
                self.set_wavelength_from_file(file)

        basicSetting = self.window.get_basic_setting()
        specHandler = SpectrumHandler(basicSetting, parameter=file.parameter)
        errorcode = specHandler.analyse_data(file)
        if not errorcode:
            if not silent:
                dialog.critical_invalidSpectrum()
            return

        self.show_wavelength_difference_information(file, basicSetting)

        self.window.set_results(specHandler)

        self.update_spectra(specHandler)
        self.activeFile = file;


    def set_wavelength_from_file(self, file:FileReader)->None:
        try:
            self.window.wavelength = file.WAVELENGTH
        except KeyError:
            self.logger.debug(f"No Wavelength provided by: {file.filename}")


    def show_wavelength_difference_information(self, file:FileReader, basicSetting:BasicSetting):
        try:
            hasDifferentWl = (float(file.WAVELENGTH) != basicSetting.wavelength)
        except KeyError:
            hasDifferentWl = False
        finally:
            self.window.show_diff_wavelength(hasDifferentWl)


    def update_spectra(self, SpectrumHandler:SpectrumHandler):
        data = SpectrumHandler.rawData.transpose()
        baseline = SpectrumHandler.baseline
        processedData = SpectrumHandler.procData.transpose()
        rawIntegration, procIntegration = SpectrumHandler.get_integration_areas()

        self.rawSpectrum.update_data(data, rawIntegration, baselineData=baseline)
        self.processedSpectrum.update_data(processedData, procIntegration)

        self.draw_spectra(self.rawSpectrum, self.processedSpectrum)


    ### Draw Plots.

    def draw_spectra(self, *spectra):
        for spectrum in spectra:
            spectrum.plot_spectrum()
