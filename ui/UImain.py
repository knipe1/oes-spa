#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Class extends the qt functionality and is contains ui elements and corresponing
interfaces


Usage:
    from ui.UImain import UIMain
    self.window = UIMain(parent)  # parent as main window or application


Glossary:



Created on Fri Jan 27 2020

@author: Hauke Wernecke
"""


# standard libs
import logging
import os

# third-party libs
from PyQt5.QtCore import QObject, pyqtSlot

# local modules/libs
from .ui_main_window import Ui_main
from .matplotlibwidget import MatplotlibWidget
from loader.configloader import ConfigLoader
from loader.yamlloader import YamlLoader
import modules.universal as uni
from modules.dataanalysis.fitting import Fitting
from modules.dataanalysis.spectrumhandler import SpectrumHandler
from modules.filehandling.filereading.filereader import FileReader
from modules.fitting_watchdog import FittingWatchdog

# enums and dataclasses
from c_types.basicsetting import BasicSetting
from c_enum.characteristic import CHARACTERISTIC as CHC


CALIBRATION_ERROR = "Calibration Error"


class UIMain(Ui_main, QObject):
    """
    Provides an interface for the UI of the main window.

    Extends the generated Qt class for the ui. Therefore methods, attributes
    and handling can be inserted and is not overwritten whenever the ui is
    updated.
    Provides interfaces to connect methods of other classes to signals of the
    ui elements. And provides also methods to connect signals to slots of ui
    elements under certain conditions.

    Usage:
        from ui.UImain import UIMain
        self.window = UIMain(parent)  # parent as main window or application


    Attributes
    ----------
    _fittings : list[str]
        Containing the filenames of the fittings.

    Methods
    -------
    _retrieve_fittings():
        Gets the fittings of the directory.
    connect_export_raw(fun):
        Interface to connect fun to triggered signal of the button.
    connect_export_processed(fun):
        Interface to connect fun to triggered signal of the button.
    connect_show_batch(fun):
        Interface to connect fun to triggered signal of the button.
    connect_open_file(fun):
        Interface to connect fun signal of the button and action.
    connect_select_fitting(fun):
        Interface to connect fun to text changed signal of the dropdown.
    connect_results(signals:dict):
        Connect given signals to corresponding ui elements.
    """

    # Load the configuration for fitting properties.
    config = ConfigLoader()
    FITTING = config.FITTING

    # Slots

    @pyqtSlot(bool)
    def enable_dispersion(self, enable:bool)->None:
        self.lblDispersion.setVisible(enable)
        self.tinDispersion.setVisible(enable)
        self.tinDispersion.setEnabled(enable)


    @pyqtSlot(bool)
    def show_diff_wavelength(self, show:bool)->None:
        """Show or hide the note whether there is a wavelength difference or not."""
        uiElement = self.lblDiffWavelength
        if show:
            uiElement.show()
        else:
            uiElement.hide()


    ### properties

    @property
    def wavelength(self)->float:
        """Get the converted wavelength or None."""
        try:
            wavelength = self.tinCentralWavelength.text()
            return float(wavelength)
        except:
            self.logger.error("Could not get valid value for wavelength!")
        return None

    @wavelength.setter
    def wavelength(self, wl:(float, str))->None:
        """Sets the given wavelenght wl to the ui-element."""
        self.tinCentralWavelength.setText(str(wl))


    @property
    def dispersion(self)->float:
        """Get the converted dispersion or None."""
        try:
            dispersion = self.tinDispersion.text()
            return float(dispersion)
        except ValueError:
            self._logger.error("Could not get valid value for dispersion!")

    @dispersion.setter
    def dispersion(self, value:(float, str))->None:
        """Sets the given wavelenght dispersion to the ui-element."""
        self.tinDispersion.setText(str(value))


    @property
    def calibration(self)->bool:
        """Get the converted calibration or None."""
        try:
            calibration = self.rcbCalibration.isChecked()
            return bool(calibration)
        except ValueError:
            self._logger.error("Could not get valid value for calibration!")

    @calibration.setter
    def calibration(self, value:(bool, str))->None:
        """Sets the given wavelenght calibration to the ui-element."""
        self.rcbCalibration.setChecked(bool(value))


    @property
    def fittings(self)->dict:
        """fittings getter"""
        return self._fittings

    @fittings.setter
    def fittings(self, fits:dict):
        """
        Add the fittings to the list.

        Updates the ui
        """
        self._fittings = fits
        self.clistFitting.addItems(fits.values())


    @property
    def plotRawSpectrum(self)->MatplotlibWidget:
        return self.mplRaw

    @property
    def plotProcessedSpectrum(self)->MatplotlibWidget:
        return self.mplProcessed


    ### methods

    def __init__(self, parent)->None:
        """

        Parameters
        ----------
        parent : QMainWindow
            The "parent" of this GUI. It is used for connections to other GUIs
            other (rather general) functions.
        """
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)

        self.setupUi(parent)
        self.__post_init__()



    def __post_init__(self):
        # Get default label for fittings, defined in Qt-designer.
        self.DEF_LBL_FITTING = self.lblFitting.text()
        self.DEF_LBL_CHARACTERISTIC = self.lblCharacteristicValue.text()

        self.DEF_LBL_CALIBRATION = "Enable Calibration"
        self.rcbCalibration.setText(self.DEF_LBL_CALIBRATION)

        self.fittings = self._retrieve_fittings()
        self._load_fitting_selection_from_config()
        self._load_settings_from_config()


    def _load_settings_from_config(self)->None:
        self.wavelength = self.config.wavelength
        self.dispersion = self.config.dispersion
        self.calibration = self.config.calibration


    def _load_fitting_selection_from_config(self)->None:
        """Loads the selected and checked fittings from the config."""
        allTexts  = self.clistFitting.allTexts()
        self._load_selected_fittings(entries=allTexts)
        self._load_checked_fittings(entries=allTexts)



    def _load_selected_fittings(self, entries:list)->None:
        """Loads the fittings from the config."""
        try:
            preIdx = entries.index(self.config.PRESELECT_FITTING)
            self.clistFitting.setCurrentRow(preIdx)
        except ValueError:
            self._logger.info("No preselected Fitting found.")


    def _load_checked_fittings(self, entries:list)->None:
        """Load the checked fittings from the config."""
        for fit in self.config.CHECKED_FITTINGS:
            try:
                ckdIdx = entries.index(fit)
                # Check the correponding checkbox.
                self.clistFitting.item(ckdIdx).setCheckState(2)
            except ValueError:
                self._logger.info("Checked fitting not found.")



    def get_results(self)->dict:
        """Retrive the Height, area, baseline and characteristic value as dict."""
        return {
            CHC.PEAK_HEIGHT.value: self.toutPeakHeight.text(),
            CHC.PEAK_AREA.value: self.toutPeakArea.text(),
            CHC.BASELINE.value: self.toutBaseline.text(),
            self.lblCharacteristicValue.text(): self.toutCharacteristicValue.text(),
        }


    def set_results(self, spectrumHandler:SpectrumHandler)->None:
        self._set_result_values(spectrumHandler)
        self._set_peak_name(spectrumHandler)
        self._set_calibration_shift(spectrumHandler)


    def _set_result_values(self, spectrumHandler:SpectrumHandler)->None:
        cwlInfo = self._get_peak_information(spectrumHandler)

        self.toutPeakHeight.setText(format_result(spectrumHandler.results[CHC.PEAK_HEIGHT]) + cwlInfo)
        self.toutPeakArea.setText(format_result(spectrumHandler.results[CHC.PEAK_AREA]))
        self.toutBaseline.setText(format_result(spectrumHandler.results[CHC.BASELINE]))
        self.toutCharacteristicValue.setText(format_result(spectrumHandler.results[CHC.CHARACTERISTIC_VALUE]))


    def _get_peak_information(self, spectrumHandler:SpectrumHandler)->str:
        """
        Gets the peak position if fitted. 0.0 otherwise.
        Returns the formatted value.
        """
        if spectrumHandler.peakPosition:
            cwl = spectrumHandler.peakPosition
        else:
            try:
                cwl = spectrumHandler.fitting.peak.centralWavelength
            except AttributeError:
                cwl = 0.0
        return f" (@{format_result(cwl)})"


    def _set_peak_name(self, spectrumHandler:SpectrumHandler)->None:
        """Sets the peak name if fitted. Default otherwise."""
        try:
            peakName = spectrumHandler.fitting.peak.name + ":"
        except AttributeError:
            peakName = self.DEF_LBL_CHARACTERISTIC
        self.lblCharacteristicValue.setText(peakName)


    def _set_calibration_shift(self, spectrumHandler:SpectrumHandler)->None:
        """Sets the shift or an error message."""
        shift = spectrumHandler.results[CHC.CALIBRATION_SHIFT]
        if self.rcbCalibration.isChecked():
            if shift is None:
                info = uni.mark_bold_red(CALIBRATION_ERROR)
            else:
                info = format_shift(shift)
        else:
            info = None

        self.rcbCalibration.setText(self.DEF_LBL_CALIBRATION, info)


    # Connect methods: Provides at least one event (signal) to connect to a
    # function
    # act: option in a dropdown of the menu bar
    # btn : Button
    # fun : function/method
    def connect_export_raw(self, fun):
        """Interface to connect fun to triggered signal of the button."""
        self.actSaveRaw.triggered.connect(fun)


    def connect_export_processed(self, fun):
        """Interface to connect fun to triggered signal of the button."""
        self.actSaveProcessed.triggered.connect(fun)


    def connect_show_batch(self, fun):
        """Interface to connect fun to triggered signal of the button."""
        self.actOpenBatch.triggered.connect(fun)


    def connect_open_file(self, fun):
        """Interface to connect fun of the button and action."""
        self.btnFileOpen.clicked.connect(fun)
        self.actOpen.triggered.connect(fun)


    def connect_change_basic_settings(self, fun):
        """Interface to connect fun to changes of the basic setting."""
        self.tinCentralWavelength.textChanged.connect(fun)
        self.tinDispersion.textChanged.connect(fun)
        self.cbInvertSpectrum.stateChanged.connect(fun)
        self.cbBaselineCorrection.stateChanged.connect(fun)
        self.cbNormalizeData.stateChanged.connect(fun)
        self.rcbCalibration.stateChanged.connect(fun)
        self.clistFitting.itemClicked.connect(fun)
        # Activate Watchdog to detect changes in fitting files.
        self._wd = FittingWatchdog(fun, directory=self.FITTING["DIR"])
        self._wd.start()


    @pyqtSlot(FileReader)
    def update_fileinformation(self, reader:FileReader)->None:
        self._set_fileinformation(reader)
        self._update_parameter(reader.parameter)
        self._enable_export(bool(reader))


    def _set_fileinformation(self, filereader:FileReader)->None:
        filename, timeInfo = filereader.fileinformation
        strTimeInfo = uni.timestamp_to_string(timeInfo)
        self.toutFilename.setText(filename)
        self.toutTimeInfo.setText(strTimeInfo)


    def _update_parameter(self, info:dict)->None:
        """
        Resets the information box and update it with the given information.

        Parameters
        ----------
        info : dict
            Information of the form: description->value.

        """
        form = ": "
        self.listInformation.clear()
        for key, value in info.items():
            entry = str(key) + form + str(value)
            self.listInformation.addItem(entry)


    def _retrieve_fittings(self) -> list:
        """
        Retrieve all fitting files of the directory of fittings.

        Requirements: Path and pattern of fitting files provided by the config file.
            UI element to display the fitting names.
            Interface to connect the event to a load currently selected fitting method/function.

        Returns
        -------
        fitList : list
            Containing the filenames of the fittings.

        """
        fitDict = {}
        # Check out the default directory for fittings.
        for _, _, f in os.walk(self.FITTING["DIR"]):
            for file in f:
                # TODO: Refactor!
                # Get the fitting files matching the pattern.
                if file.rfind(self.FITTING["FILE_PATTERN"]) > -1:
                    # loading the parameter and set up the dict using the
                    # filename and the name of the fitting
                    path = os.path.join(self.FITTING["DIR"], file)
                    fitConfig = YamlLoader(path)

                    fit = fitConfig.config.get("NAME", "no name def.")
                    fitDict[file] = fit

        return fitDict


    def _load_fitting(self, fittingName:str, showError:bool=False)->Fitting:
        """
        Parameters
        ----------
        fittingName : str
            The name of the selected fitting within the ui element.

        Returns
        -------
        activeFitting : Fitting
        """

        self._logger.info("Load fitting: %s", fittingName)

        filename = self._get_filename_of_fitting(fittingName)
        fitConfig = self._load_fitting_configuration(filename)
        try:
            activeFitting = Fitting(fitConfig.config, filename)
        except AttributeError:
            # If no config was loaded.
            return None
        if showError:
            self._set_fittings_errorcode(activeFitting)
        return activeFitting


    def _enable_export(self, enable:bool)->None:
        self.actSaveRaw.setEnabled(enable)
        self.actSaveProcessed.setEnabled(enable)


    def get_basic_setting(self)->BasicSetting:
        """Gets the current options of the setting and setup a new BasicSetting."""
        selectedFitting = self._load_fitting(self.clistFitting.currentText(), showError=True)
        checkedFittings = self.clistFitting.checkedItems()
        checkedFittings = [self._load_fitting(t.text()) for t in checkedFittings]
        invertSpectrum = self.cbInvertSpectrum.isChecked()
        baselineCorrection = self.cbBaselineCorrection.isChecked()
        normalizeData = self.cbNormalizeData.isChecked()
        calibration = self.rcbCalibration.isChecked()
        setting = BasicSetting(wavelength=self.wavelength, dispersion=self.dispersion, invertSpectrum=invertSpectrum,
                               selectedFitting=selectedFitting, checkedFittings=checkedFittings,
                               baselineCorrection=baselineCorrection, normalizeData=normalizeData, calibration=calibration)

        return setting


    def _get_filename_of_fitting(self, fittingName:str)->str:
        for fitFilename, fitName in self.fittings.items():
            if fitName == fittingName:
                return fitFilename
        return None


    def _load_fitting_configuration(self, filename:str)->Fitting:
        try:
            path = os.path.join(self.FITTING["DIR"], filename)
        except TypeError:
            # E.g. if no filename is given (no fitting is selected.)
            return None
        fitConfig = YamlLoader(path)
        return fitConfig


    def _set_fittings_errorcode(self, fit:Fitting):
        label = uni.mark_bold_red(fit.errCode) + self.DEF_LBL_FITTING
        self.lblFitting.setText(label)


    def save_settings(self)->None:
        self._save_wavelength_and_dispersion()
        self._save_selected_fitting()


    def _save_wavelength_and_dispersion(self)->None:
        self.config = ConfigLoader()
        self.config.wavelength = self.wavelength
        self.config.dispersion = self.dispersion
        self.config.calibration = self.calibration
        self.config.save_config()


    def _save_selected_fitting(self):
        selectedFitting = self.clistFitting.currentText()
        self._logger.info("Save selected fitting: %s.", selectedFitting)

        checkedFittings = self.clistFitting.checkedItems()
        checkedFittings = [t.text() for t in checkedFittings]
        self._logger.info("Save checked fittings: %s.", checkedFittings)

        self.config = ConfigLoader()
        self.config.PRESELECT_FITTING = selectedFitting
        self.config.CHECKED_FITTINGS = checkedFittings
        self.config.save_config()


def format_result(value:float)->str:
    try:
        return f"{value:8.4f}"
    except TypeError:
        return str(None)


def format_shift(shift:float)->str:
    return f"(Δ {shift:.3f})"
