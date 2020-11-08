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
import os

# third-party libs
from dependencies.natsort.natsort import natsorted

# local modules/libs
from ui.ui_main_window import Ui_main
from ConfigLoader import ConfigLoader
from modules.dataanalysis.Fitting import Fitting
from Logger import Logger
import modules.Universal as uni
from modules.Universal import mark_bold_red
from ui.matplotlibwidget import MatplotlibWidget
from modules.dataanalysis.SpectrumHandler import SpectrumHandler
from modules.filehandling.filereading.FileReader import FileReader

# enums and dataclasses
from custom_types.BasicSetting import BasicSetting
from c_enum.CHARACTERISTIC import CHARACTERISTIC as CHC

class UIMain(Ui_main):
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
    UI_MAPPING : dict
        Maps general keys to specific ui elements.

    Methods
    -------
    retrieve_fittings():
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
    FITTING = config.FITTING;

    ### properties

    @property
    def wavelength(self)->float:
        """Get the converted wavelength or None."""
        # TODO: try/except vs throw an error?
        # try: no exception and the program can still run
        # error: is it an error, if the ui element is not found -> prob. yes
        # error: if something invalid is written? -> prompt
        wavelength = None
        try:
            wavelength = self.tinCentralWavelength.text()
            wavelength = float(wavelength)
        except:
            self.logger.error("Could not get valid value for wavelength!")
        return wavelength

    @wavelength.setter
    def wavelength(self, wl):
        """Sets the given wavelenght wl to the ui-element."""
        self.tinCentralWavelength.setText(wl)


    @property
    def grating(self)->int:
        """Get the converted grating or None."""
        # TODO: cf. wavelength, but dropdown cannot be empty.
        grating = None
        try:
            grating = self.ddGrating.currentText()
            grating = float(grating)
        except:
            self.logger.error("Could not get valid value for grating!")
        return grating


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
        try:
            uiElement = self.ddFitting
            uiElement.clear()
            sortedFits = natsorted(fits.values())
            uiElement.addItems(sortedFits)
        except:
            pass

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
        # set up the logger
        self.logger = Logger(__name__)

        self.setupUi(parent)
        self.__post_init__()


    def __post_init__(self):
        # Get default label for fittings, defined in Qt-designer.
        self.DEF_LBL_FITTING = self.lblFitting.text()

        self.fittings = self.retrieve_fittings()
        self.ddFitting.currentTextChanged.connect(self.load_fitting)
        try:
            self.ddFitting.setCurrentText(self.FITTING["fittingName"])
        except KeyError:
            pass
        # initial hides. Cannot be set in designer.
        self.show_diff_wavelength(False)


    def get_results(self):
        results = {CHC.PEAK_HEIGHT.value: self.toutPeakHeight.text(),
                   CHC.PEAK_AREA.value: self.toutPeakArea.text(),
                   CHC.BASELINE.value: self.toutBaseline.text(),
                   self.lblCharacteristicValue.text(): self.toutCharacteristicValue.text(),
                   }
        return results


    def set_results(self, spectrumHandler:SpectrumHandler):
        self.toutPeakHeight.setText(str(spectrumHandler.peakHeight))
        self.toutPeakArea.setText(str(spectrumHandler.peakArea))
        self.toutBaseline.setText(str(spectrumHandler.avgbase))
        self.toutCharacteristicValue.setText(str(spectrumHandler.characteristicValue))
        peakName = spectrumHandler.fitting.peak.name
        self.lblCharacteristicValue.setText(str(peakName))


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
        self.ddGrating.currentTextChanged.connect(fun)
        self.ddFitting.currentTextChanged.connect(fun)
        self.cbBaselineCorrection.stateChanged.connect(fun)
        self.cbNormalizeData.stateChanged.connect(fun)
        self.clistFitting.itemClicked.connect(fun)


    def set_fileinformation(self, filereader:FileReader)->None:
        filename, timeInfo = filereader.fileinformation
        strTimeInfo = uni.timestamp_to_string(timeInfo)
        self.toutFilename.setText(filename)
        self.toutTimeInfo.setText(strTimeInfo)


    def retrieve_fittings(self) -> list:
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
                    fitConfig = ConfigLoader(path)

                    fit = fitConfig.config.get("NAME", "no name def.")
                    fitDict[file] = fit

        return fitDict


    def load_fitting(self, fittingName:str)->Fitting:
        """
        Parameters
        ----------
        fittingName : str
            The name of the selected fitting within the ui element.

        Returns
        -------
        activeFitting : Fitting
        """

        self.logger.info("Load fitting: " + fittingName)

        filename = self.get_filename_of_fitting(fittingName)
        fitConfig = self.get_fitting_configuration(filename)
        activeFitting = Fitting(fitConfig.config)
        self.set_fittings_errorcode(activeFitting)
        return activeFitting


    def update_information(self, info:dict)->None:
        """
        Resets the information box and update it with the given information.

        Parameters
        ----------
        info : dict
            Information of the form: description->value.

        """
        # Init Format and clear.
        form = ": "
        self.listInformation.clear()
        for line in info.items():
            # format the entry
            entry = form.join(line)
            self.listInformation.addItem(entry)


    def show_diff_wavelength(self, show:bool):
        uiElement = self.lblDiffWavelength
        if show:
            uiElement.show()
        else:
            uiElement.hide()


    def enable_export(self, enable:bool)->None:
        self.actSaveRaw.setEnabled(enable)
        self.actSaveProcessed.setEnabled(enable)


    def get_basic_setting(self)->BasicSetting:
        baselineCorrection = self.cbBaselineCorrection.isChecked()
        normalizeData = self.cbNormalizeData.isChecked()
        fitting = self.load_fitting(self.ddFitting.currentText())
        selectedFitting = self.load_fitting(self.clistFitting.currentText())
        checkedFittings = self.clistFitting.checkedItems()
        checkedFittings = [self.load_fitting(t.text()) for t in checkedFittings]
        # setting = BasicSetting(self.wavelength, self.grating, fitting, baselineCorrection, normalizeData)
        setting = BasicSetting(self.wavelength, self.grating, selectedFitting, checkedFittings, baselineCorrection, normalizeData)

        return setting;


    def get_filename_of_fitting(self, fittingName:str)->str:
        for fitFilename, fitName in self.fittings.items():
            if fitName == fittingName:
                return fitFilename


    def get_fitting_configuration(self, filename:str):
        path = os.path.join(self.FITTING["DIR"], filename)
        fitConfig = ConfigLoader(path)
        return fitConfig


    def set_fittings_errorcode(self, fit:Fitting):
        label = mark_bold_red(fit.errCode) + self.DEF_LBL_FITTING
        self.lblFitting.setText(label)


    def save_selected_fitting(self):
        fitName = self.ddFitting.currentText()
        self.logger.info(f"Save fitting: {fitName}.")
        self.config = ConfigLoader()
        self.config.fittingName = fitName
        self.config.save_config()
