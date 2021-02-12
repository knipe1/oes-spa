#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Class extends the qt functionality and is contains ui elements and corresponing
interfaces


Usage:
    from ui.UIMain import UIMain
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
from ui.ui_main_window import Ui_main
from ui.matplotlibwidget import MatplotlibWidget
from loader.ConfigLoader import ConfigLoader
from loader.YamlLoader import YamlLoader
import modules.Universal as uni
from modules.dataanalysis.Fitting import Fitting
from modules.dataanalysis.SpectrumHandler import SpectrumHandler
from modules.filehandling.filereading.FileReader import FileReader

# enums and dataclasses
from c_types.BasicSetting import BasicSetting
from c_enum.CHARACTERISTIC import CHARACTERISTIC as CHC


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
        from ui.UIMain import UIMain
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
    def slot_enableDispersion(self, enable:bool)->None:
        self.tinDispersion.setEnabled(enable)


    @pyqtSlot(bool)
    def slot_show_diff_wavelength(self, show:bool)->None:
        uiElement = self.lblDiffWavelength
        if show:
            uiElement.show()
        else:
            uiElement.hide()


    ### properties

    @property
    def wavelength(self)->float:
        """Get the converted wavelength or None."""
        wavelength = None
        try:
            wavelength = self.tinCentralWavelength.text()
            wavelength = float(wavelength)
        except ValueError:
            self._logger.error("Could not get valid value for wavelength!")
        return wavelength

    @wavelength.setter
    def wavelength(self, wl:(float, str))->None:
        """Sets the given wavelenght wl to the ui-element."""
        self.tinCentralWavelength.setText(str(wl))


    @property
    def dispersion(self)->float:
        """Get the converted dispersion or None."""
        dispersion = None
        try:
            dispersion = self.tinDispersion.text()
            dispersion = float(dispersion)
        except ValueError:
            self._logger.error("Could not get valid value for dispersion!")
        return dispersion

    @dispersion.setter
    def dispersion(self, disp:(float, str))->None:
        """Sets the given wavelenght dispersion to the ui-element."""
        self.tinDispersion.setText(str(disp))


    @property
    def fittings(self)->dict:
        """fittings getter"""
        return self._fittings

    @fittings.setter
    def fittings(self, fits:dict):
        """fittings setter

        Updating the ui
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
        self.DEF_LBL_CALIBRATION = self.cbCalibration.text()

        self.fittings = self._retrieve_fittings()
        self._load_fitting_selection_from_config()
        self._load_settings_from_config()


    def _load_settings_from_config(self)->None:
        self.wavelength = self.config.wavelength
        self.dispersion = self.config.dispersion


    def _load_fitting_selection_from_config(self)->None:
        allTexts  = self.clistFitting.allTexts()
        PRESELECT_FITTING = self.config.PRESELECT_FITTING
        try:
            preIdx = allTexts.index(PRESELECT_FITTING)
            self.clistFitting.setCurrentRow(preIdx)
        except ValueError:
            self._logger.info("No preselected Fitting found.")

        CHECKED_FITTINGS = self.config.CHECKED_FITTINGS
        for fit in CHECKED_FITTINGS:
            try:
                ckdIdx = allTexts.index(fit)
                self.clistFitting.item(ckdIdx).setCheckState(2)
            except ValueError:
                self._logger.info("Checked fitting not found.")


    def get_results(self):
        results = {CHC.PEAK_HEIGHT.value: self.toutPeakHeight.text(),
                   CHC.PEAK_AREA.value: self.toutPeakArea.text(),
                   CHC.BASELINE.value: self.toutBaseline.text(),
                   self.lblCharacteristicValue.text(): self.toutCharacteristicValue.text(),
                   }
        return results


    def set_results(self, spectrumHandler:SpectrumHandler):
        if spectrumHandler.peakPosition:
            cwl = spectrumHandler.peakPosition
        else:
            try:
                cwl = spectrumHandler.fitting.peak.centralWavelength
            except AttributeError:
                cwl = 0.0
        cwlInfo = f" (@{format_result(cwl)})"

        self.toutPeakHeight.setText(
            format_result(spectrumHandler.results[CHC.PEAK_HEIGHT]) + cwlInfo)
        self.toutPeakArea.setText(format_result(spectrumHandler.results[CHC.PEAK_AREA]))
        self.toutBaseline.setText(format_result(spectrumHandler.results[CHC.BASELINE]))
        self.toutCharacteristicValue.setText(
            format_result(spectrumHandler.results[CHC.CHARACTERISTIC_VALUE]))
        try:
            peakName = spectrumHandler.fitting.peak.name + ":"
        except AttributeError:
            peakName = self.DEF_LBL_CHARACTERISTIC
        self.lblCharacteristicValue.setText(peakName)

        shift = spectrumHandler.results[CHC.CALIBRATION_SHIFT] or 0.0
        calibrationLabel = self.DEF_LBL_CALIBRATION + format_shift(shift)
        self.cbCalibration.setText(calibrationLabel)






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
        self.cbBaselineCorrection.stateChanged.connect(fun)
        self.cbNormalizeData.stateChanged.connect(fun)
        self.cbCalibration.stateChanged.connect(fun)
        self.clistFitting.itemClicked.connect(fun)


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
        for line in info.items():
            entry = form.join(line)
            self.listInformation.addItem(entry)


    def _retrieve_fittings(self) -> list:
        """
        Retrieve all fitting files of the directory of fittings.

        Requirements: Path and pattern of fitting files provided by the config
            file.
            UI element to display the fitting names.
            Interface to connect the event to a load currently selected
            fitting method/function.

        Returns
        -------
        fitList : list
            Containing the filenames of the fittings.

        """
        fitDict = {}
        # Check out the default directory for fittings.
        for _, _, f in os.walk(self.FITTING["DIR"]):
            for file in f:
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
            activeFitting = Fitting(fitConfig.config)
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
        selectedFitting = self._load_fitting(self.clistFitting.currentText(), showError=True)
        checkedFittings = self.clistFitting.checkedItems()
        checkedFittings = [self._load_fitting(t.text()) for t in checkedFittings]
        baselineCorrection = self.cbBaselineCorrection.isChecked()
        normalizeData = self.cbNormalizeData.isChecked()
        calibration = self.cbCalibration.isChecked()
        setting = BasicSetting(self.wavelength, self.dispersion, selectedFitting, checkedFittings,
                               baselineCorrection, normalizeData, calibration)

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
        wl = self.wavelength
        dp = self.dispersion

        self.config = ConfigLoader()
        self.config.wavelength = wl
        self.config.dispersion = dp
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
    return f"\n(Δ {shift:.3f})"
