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
# base class: QMainWindow
from PyQt5.QtWidgets import QMainWindow

# local modules/libs
from ui.UIMain import UIMain
from ConfigLoader import ConfigLoader
from Logger import Logger
import dialog_messages as dialog
import modules.Universal as uni
from modules.BatchAnalysis import BatchAnalysis
from modules.dataanalysis.Spectrum import Spectrum
from modules.dataanalysis.SpectrumHandler import SpectrumHandler
from modules.filehandling.filereading.FileReader import FileReader
from modules.filehandling.filewriting.SpectrumWriter import SpectrumWriter

# enums
from c_types.BasicSetting import BasicSetting
from c_enum.EXPORT_TYPE import EXPORT_TYPE
from c_enum.ERROR_CODE import ERROR_CODE as ERR

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
        self.window.enable_export(bool(file))

        self._activeFile = file


    @property
    def lastdir(self)->str:
        """Gets the directory which is preset for dialogs."""
        return self._lastdir

    @lastdir.setter
    def lastdir(self, directory:str)->None:
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


    def __post_init__(self)->None:
        self.connect_ui_events()
        self.init_spectra()


    def __repr__(self):
        info = {}
        info["activeFile"] = self.activeFile
        info["lastdir"] = self.lastdir
        return self.__module__ + ":\n" + str(info)


    def init_spectra(self)->None:
        """Set up the Spectrum elements with the corresponding ui elements."""
        self.rawSpectrum = Spectrum(self.window.plotRawSpectrum, EXPORT_TYPE.RAW)
        self.processedSpectrum = Spectrum(self.window.plotProcessedSpectrum, EXPORT_TYPE.PROCESSED);


    def connect_ui_events(self)->None:
        win = self.window
        win.connect_change_basic_settings(self.redraw)
        win.connect_export_raw(self.export_raw)
        win.connect_export_processed(self.export_processed)
        win.connect_open_file(self.file_open)
        win.connect_show_batch(self.batch.show)


    ### Events

    def closeEvent(self, event)->None:
        """Closing the BatchAnalysis dialog to have a clear shutdown."""
        self.batch.close()
        self.window.save_selected_fitting()


    def dragEnterEvent(self, event)->None:
        # Handle the urls. Multiple urls are handled by BatchAnalysis.
        urls = event.mimeData().urls();
        isSingleFile = (len(urls) == 1)
        isMultipleFiles =(len(urls) > 1)

        if isMultipleFiles:
            self.batch.show();
        elif isSingleFile:
            event.accept()


    def dropEvent(self, event)->None:
        event.accept();

        # Can only be one single file.
        url = event.mimeData().urls()[0];
        localUrl = uni.get_valid_local_url(url)

        if localUrl:
            self.apply_file(localUrl)
        else:
            dialog.critical_unknownSuffix(parent=self)


    ### Methods

    def file_open(self)->None:
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
        else:
            return

        self.lastdir = filelist[0]


    ### Export

    def export_raw(self)->None:
        self.export_spectrum(self.rawSpectrum)


    def export_processed(self)->None:
        results = self.window.get_results();
        self.export_spectrum(self.processedSpectrum, results)


    def export_spectrum(self, spectrum:Spectrum, results:dict={})->None:

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


    def redraw(self, changedValue:str=None)->None:
        """
        Redraw the plots with data of the active file.

        Parameters
        ----------
        changedValue : str
            The value of the new selected option. Informative in the logger.

        """
        try:
            self.logger.info(f"New value of setting: {changedValue}. Redraw of {self.activeFile.filename}.")
            self.apply_file(self.activeFile)
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
        errorcode = specHandler.analyse_data(file, basicSetting.selectedFitting)
        if errorcode or errorcode == ERR.NO_FITTING:
            self.update_spectra(specHandler)
            self.activeFile = file;
        else:
            if not silent:
                dialog.critical_invalidSpectrum()
            return

        self.show_wavelength_difference_information(file, basicSetting)
        self.window.set_results(specHandler)


    def set_wavelength_from_file(self, file:FileReader)->None:
        try:
            self.window.wavelength = file.WAVELENGTH
        except KeyError:
            self.logger.debug(f"No Wavelength provided by: {file.filename}")


    def show_wavelength_difference_information(self, file:FileReader, setting:BasicSetting)->None:
        settingWavelength = setting.wavelength
        try:
            fileWavelength = float(file.WAVELENGTH)
        except KeyError:
            fileWavelength = None
            settingWavelength = None
        finally:
            hasDifferentWl = (fileWavelength != settingWavelength)
            self.window.show_diff_wavelength(hasDifferentWl)


    def update_spectra(self, SpectrumHandler:SpectrumHandler):
        data = SpectrumHandler.rawData
        baseline = SpectrumHandler.baseline
        processedData = SpectrumHandler.procData
        rawIntegration, procIntegration = SpectrumHandler.get_integration_areas()

        self.rawSpectrum.update_data(data, rawIntegration, baselineData=baseline)
        self.processedSpectrum.update_data(processedData, procIntegration)
