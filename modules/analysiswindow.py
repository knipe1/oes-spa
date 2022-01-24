#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Glossary:
        - activeFile:
            The file that is "active" (plotted and the results shown are analyzed from this file.)

@author: Hauke Wernecke
"""

# standard libs
import logging

# third-party libs
# base class: QMainWindow
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow


# local modules/libs
from ui.UImain import UIMain
import dialog_messages as dialog
import modules.universal as uni
from .batchanalysis import BatchAnalysis
from .dataanalysis.spectrum import Spectrum
from .dataanalysis.spectrumhandler import SpectrumHandler
from .filehandling.filereading.filereader import FileReader
from .filehandling.filewriting.spectrumwriter import SpectrumWriter

# enums
from c_types.basicsetting import BasicSetting
from c_enum.export_type import EXPORT_TYPE
from c_enum.characteristic import CHARACTERISTIC as CHC

# constants

# exceptions
from exception.InvalidSpectrumError import InvalidSpectrumError
from exception.ParameterNotSetError import ParameterNotSetError
from exception.CalibrationError import CalibrationError


class AnalysisWindow(QMainWindow):
    """
    Main Window. Organization and interfaces of sub-types/sub-windows.

    Usage:
        from modules.analysiswindow import AnalysisWindow
        window = AnalysisWindow()
        window.apply_file("./sample files/Asterix1059 1.Spk") # Load a spectrum programmatically.
    """

    ### Signal

    wavelengthChanged = pyqtSignal(bool)
    fileChanged = pyqtSignal(FileReader)


    ### Slots

    @pyqtSlot(str)
    @pyqtSlot(FileReader, bool)
    def plot_spectrum(self, file:str, silent_:bool=True)->None:
        self.apply_file(file, silent=silent_)


    @pyqtSlot()
    def setting_changed(self, *args, **kwargs):
        self.setting = self.window.get_basic_setting()


    ### Properties

    @property
    def activeFile(self)->FileReader:
        """activeFile getter"""
        return self._activeFile

    @activeFile.setter
    def activeFile(self, file:FileReader)->None:
        """activeFile setter: Updating the ui"""
        if file != self._activeFile:
            self.fileChanged.emit(file)
        self._activeFile = file


    @property
    def setting(self)->BasicSetting:
        return self._setting

    @setting.setter
    def setting(self, s:BasicSetting)->None:
        self._setting = s
        self._redraw()
        self.batch.set_setting(s)




    ### __Methods__

    def __init__(self)->None:
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)

        # Defaults.
        self._activeFile = None

        ## Set up the UI
        self.window = UIMain(self)
        self.batch = BatchAnalysis(self)

        self.__post_init__()

        # Hide initially. Cannot be set in designer.
        self.wavelengthChanged.emit(False)

        # Show window, otherwise the window does not appear anywhere on the screen.
        self.show()


    def __post_init__(self)->None:
        self._connect_ui_events()
        self._init_spectra()
        self.setting = self.window.get_basic_setting()


    def __repr__(self):
        info = {}
        info["activeFile"] = self.activeFile
        return self.__module__ + ":\n" + str(info)


    def _init_spectra(self)->None:
        """Set up the Spectrum elements with the corresponding ui elements."""
        self.rawSpectrum = Spectrum(self.window.plotRawSpectrum, EXPORT_TYPE.RAW)
        self.processedSpectrum = Spectrum(self.window.plotProcessedSpectrum,
                                          EXPORT_TYPE.PROCESSED)


    def _connect_ui_events(self)->None:
        win = self.window
        win.connect_change_basic_settings(self.setting_changed)
        win.connect_export_processed(self._export_processed)
        win.connect_export_raw(self._export_raw)
        win.connect_open_file(self._file_open)
        win.connect_show_batch(self.batch.show)

        self.wavelengthChanged.connect(win.show_diff_wavelength)
        self.fileChanged.connect(win.update_fileinformation)


    ### Events

    def closeEvent(self, event)->None:
        """Closes the BatchAnalysis dialog and save the settings."""
        event.accept()
        self.batch.close()
        self.window.save_settings()


    def dragEnterEvent(self, event)->None:
        # Handle the urls. Multiple urls are handled by BatchAnalysis.
        urls = event.mimeData().urls()
        isSingleFile = (len(urls) == 1)
        isMultipleFiles =(len(urls) > 1)

        if isMultipleFiles:
            self.batch.show()
        elif isSingleFile:
            event.accept()


    def dropEvent(self, event)->None:
        event.accept()

        url = event.mimeData().urls()[0]
        localUrl = uni.get_valid_local_url(url)

        if localUrl:
            self.apply_file(localUrl)
        else:
            dialog.critical_unknownSuffix(parent=self)


    ### Methods

    def _file_open(self)->None:
        """Opens a FileDialog to select one or multiple spectra."""

        # Cancel/Quit dialog --> [].
        filelist = dialog.dialog_spectra()
        isSingleFile = (len(filelist) == 1)
        isMultipleFiles = (len(filelist) > 1)

        if isMultipleFiles:
            self.batch.show()
            self.batch.update_filelist(filelist)
        elif isSingleFile:
            filename = filelist[0]
            self.apply_file(filename)


    ### Export

    def _export_raw(self)->None:
        self._export_spectrum(self.rawSpectrum)


    def _export_processed(self)->None:
        results = self.window.get_results()
        self._export_spectrum(self.processedSpectrum, results)


    def _export_spectrum(self, spectrum:Spectrum, results:dict=None)->None:
        results = results or {}

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


    def _redraw(self)->None:
        """Redraw the plots with data of the active file."""
        try:
            self._logger.info("Redraw of %s.", self.activeFile.filename)
            self.apply_file(self.activeFile)
        except AttributeError:
            self._logger.warning("Redraw Failed")


    ### data analysis

    def apply_file(self, filename:(str, FileReader), silent:bool=False)->None:
        """Read the file and displays the spectrum."""
        if not isinstance(filename, FileReader):
            file = FileReader(filename)
        else:
            file = filename

        # HINT: set wavelength triggers a redraw loop. If wavelength is set after the setting
        # is loaded, the analysis will not update the setting.
        isFileReloaded = (self.activeFile == file)
        if not isFileReloaded:
            self._set_wavelength_from_file(file)

        try:
            specHandler = SpectrumHandler(file, self.setting, slotPixel=self.window.enable_dispersion)
        except InvalidSpectrumError:
            if not silent:
                dialog.critical_invalidSpectrum()
            return

        try:
            specHandler.fit_data(self.setting.selectedFitting)
        except CalibrationError as e:
            self._logger.warning(f"{file.filename}: {e}")

        self._update_spectra(specHandler)
        self.activeFile = file

        self._show_wavelength_difference_information(file)
        self.window.set_results(specHandler)


    def _set_wavelength_from_file(self, file:FileReader)->None:
        try:
            self.window.wavelength = file.WAVELENGTH
        except ParameterNotSetError:
            self._logger.info("No Wavelength provided by: %s", file.filename)


    def _show_wavelength_difference_information(self, file:FileReader)->None:
        settingWavelength = self.setting.wavelength
        try:
            fileWavelength = file.WAVELENGTH
        except ParameterNotSetError:
            fileWavelength = None
            settingWavelength = None
        finally:
            hasDifferentWl = (fileWavelength != settingWavelength)
            self.wavelengthChanged.emit(hasDifferentWl)


    def _update_spectra(self, specHandler:SpectrumHandler)->None:
        rawIntegration, procIntegration = specHandler.get_integration_areas()

        self.rawSpectrum.set_data(specHandler.rawData, integrationAreas=rawIntegration,
                                  baselineData=specHandler.baseline)
        self.processedSpectrum.set_data(specHandler.procData, integrationAreas=procIntegration,
                                        calibrationPeaks=specHandler.results[CHC.CALIBRATION_PEAKS])