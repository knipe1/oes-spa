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

# local modules/libs
from ui.ui_main_window import Ui_main
from ConfigLoader import ConfigLoader
from modules.Fitting import Fitting
from Logger import Logger
from modules.Universal import mark_bold_red
from ui.matplotlibwidget import MatplotlibWidget
from modules.SpectrumHandler import SpectrumHandler

# enums and dataclasses
from custom_types.BasicSetting import BasicSetting
from custom_types.CHARACTERISTIC import CHARACTERISTIC as CHC

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
    init_mapping():
        Set up the mapping of ui elements and general keys.
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
            uiElement = self.UI_MAPPING["fitting"]
            uiElement.clear()
            uiElement.addItems(fits.values())
        except:
            pass

    @property
    def plotRawSpectrum(self)->MatplotlibWidget:
        return self.mplRaw

    @property
    def plotProcessedSpectrum(self)->MatplotlibWidget:
        return self.mplProcessed

    ### methods

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent : QMainWindow
            The "parent" of this GUI. It is used for connections to other GUIs
            other (rather general) functions.

        Returns
        -------
        None.

        """
        # set up the logger
        self.logger = Logger(__name__)

        self.setupUi(parent)
        self.UI_MAPPING = self.init_mapping()


        self.__post_init__()


    def __post_init__(self):
        # Get default label for fittings, defined in Qt-designer.
        self.DEF_LBL_FITTING = self.lblFitting.text()

        self.fittings = self.retrieve_fittings()
        self.connect_select_fitting(self.load_current_fitting)
        # initial hides
        self.show_diff_wavelength(False)


    # TODO: ought be immutable
    # TODO: import from somewhere? Issue: can't link to ui element
    def init_mapping(self):
        mapping = {"fitting": self.ddFitting,
                   }
        return mapping


    def get_results(self):
        results = {CHC.PEAK_HEIGHT.value: self.toutPeakHeight.text(),
                   CHC.PEAK_AREA.value: self.toutPeakArea.text(),
                   CHC.BASELINE.value: self.toutBaseline.text(),
                   self.lblCharacteristicValue.text():
                       self.toutCharacteristicValue.text(),
                   }
        return results


    def set_results(self, spectrumHandler:SpectrumHandler, peakName:str):
        self.toutPeakHeight.setText(str(spectrumHandler.peakHeight))
        self.toutPeakArea.setText(str(spectrumHandler.peakArea))
        self.toutBaseline.setText(str(spectrumHandler.avgbase))
        self.toutCharacteristicValue.setText(str(spectrumHandler.characteristicValue))
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


    def connect_select_fitting(self, fun):
        """Interface to connect fun to text changed signal of the dropdown."""
        # TODO: evaluate the pro and cons
        # Pro: ui element can be changed in one position
        # Con: Readability
        # Alternatives:
        # self.ddFitting.currentTextChanged.connect(fun)
        # self.UI_MAPPING.get("fitting").currentTextChanged.connect(fun)
        uiElement = self.UI_MAPPING["fitting"]
        uiElement.currentTextChanged.connect(fun)
        # Emit the signal once to trigger the connected methods once.
        uiElement.currentTextChanged.emit(uiElement.currentText())


    def set_fileinformation(self, filename:str, date:str, time:str)->None:
        # TODO: docstring, also add to class methods
        self.toutFilename.setText(filename)
        self.toutDate.setText(date)
        self.toutTime.setText(time)


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
        # check out the default directory for fittings
        for _, _, f in os.walk(self.FITTING["DIR"]):
            for file in f:
                # get the fitting files matching the pattern
                if file.rfind(self.FITTING["FILE_PATTERN"]) > -1:
                    # loading the parameter and set up the dict using the
                    # filename and the name of the fitting
                    path = os.path.join(self.FITTING["DIR"], file)
                    fitConfig = ConfigLoader(path)

                    fit = fitConfig.config.get("NAME", "no name def.")
                    fitDict[file] = fit
                    # fit = Fitting(fitConfig.config)
                    # fitDict[file] = fit.name

        return fitDict

    def load_current_fitting(self, fitting_name:str) -> dict:
        """
        Retrieve the config of the currently selected fitting.

        Can be connected to the signal of an ui element, e.g.
        "currentTextChanged".

        Parameters
        ----------
        fitting_name : str
            The name of the selected fitting within the ui element.

        Returns
        -------
        fitConfig : dict
            Contains the config of the selected fitting.

        """
        # TODO: another function? if so, use current_fitting as property
        # and use the other funtion?
        # TODO: check out the class Peak!
        # get the selected fitting
        self.logger.info("Load fitting.")
        for fit, name in self.fittings.items():
            if name == fitting_name:
                current_fit = fit
                break

        # load the config from the file and set the current config
        path = os.path.join(self.FITTING["DIR"], current_fit)
        fitConfig = ConfigLoader(path)

        self.currentFitting = Fitting(fitConfig.config)

        # Update UI
        label = mark_bold_red(self.currentFitting.errCode) + self.DEF_LBL_FITTING
        self.lblFitting.setText(label)


    def update_information(self, info:dict):
        """
        Resets the information box and update it with the given information.

        Parameters
        ----------
        info : dict
            Information of the form: description->value.

        Returns
        -------
        None.

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


    def get_basic_setting(self)->BasicSetting:

        grating = self.grating
        fitting = self.currentFitting
        setting = BasicSetting(self.wavelength, grating, fitting)

        return setting;