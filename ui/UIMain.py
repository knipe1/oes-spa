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
from PyQt5.QtCore import pyqtBoundSignal

# local modules/libs
from ui.ui_main_window import Ui_main
from ConfigLoader import ConfigLoader
from modules.Fitting import Fitting
from Logger import Logger

# enums and dataclasses
from custom_types.BasicSetting import BasicSetting
from custom_types.UI_RESULTS import UI_RESULTS
from custom_types.CHARACTERISTIC import CHARACTERISTIC

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

    # set up the logger
    logger = Logger(__name__)

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
    def fittings(self)->dict:
        """fittings getter"""
        return self._fittings

    @fittings.setter
    def fittings(self, fits:dict):
        """fittings setter

        Updating the ui
        """
        self._fittings = fits
        uiElement = self.UI_MAPPING.get("fitting")

        if not uiElement is None:
            uiElement.clear()
            uiElement.addItems(fits.values())

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
        self.setupUi(parent)
        self.UI_MAPPING = self.init_mapping()
        self.__post_init__()


    def __post_init__(self):
        self.fittings = self.retrieve_fittings()
        self.connect_select_fitting(self.load_current_fitting)


    # TODO: ought be immutable
    # TODO: import from somewhere? Issue: can't link to ui element
    def init_mapping(self):
        mapping = {"fitting": self.ddFitting,
                   UI_RESULTS.tout_PEAK_HEIGHT: self.toutPeakHeight,
                   UI_RESULTS.tout_PEAK_AREA: self.toutPeakArea,
                   UI_RESULTS.tout_BASELINE: self.toutBaseline,
                   UI_RESULTS.tout_CHARACTERISTIC_VALUE:
                       self.toutCharacteristicValue,
                   UI_RESULTS.lbl_CHARACTERISTIC_VALUE:
                       self.lblCharacteristicValue,
                   }
        return mapping


    def get_results(self):
        results = {CHARACTERISTIC.PEAK_HEIGHT.value:
                       self.toutPeakHeight.text(),
                   CHARACTERISTIC.PEAK_AREA.value:
                       self.toutPeakArea.text(),
                   CHARACTERISTIC.BASELINE.value:
                       self.toutBaseline.text(),
                   self.lblCharacteristicValue.text():
                       self.toutCharacteristicValue.text(),
                   }
        return results


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



    def connect_results(self, signals:dict):
        """
        Connect given signals to corresponding ui elements.

        Parameters
        ----------
        signals : dict
            Should contain key-value pairs like the following structure: key as
            a defined key in the enum UI_RESULTS, value as a signal of a
            QtObject (pyqtBoundSignal).

        Returns
        -------
        bool
            False: No dict given/No valid key in dict.
            True: No error occured.

        """

        # No custom Exception were raised so that the program do not crash just
        # because the ui connection failed. Reports were given in the log.

        # TODO: doublecheck. Throw an error if noo dict is given?
        # Then remove upper comment and following 3 lines
        if not isinstance(signals, dict):
            self.logger.warning("connect_results: No dict given")
            return False

        # connect the signal with the corresponding ui element
        for element, signal in signals.items():
            # skip signal if not qt-signal
            if not isinstance(signal, pyqtBoundSignal):
                self.logger.info("connect_results: No valid signal")
                continue
            # skip key if not defined in enum
            if not isinstance(element, UI_RESULTS):
                self.logger.info("connect_results: No valid element")
                continue

            # if a ui element is linked to that element, the signal is
            # connected
            uiElement = self.UI_MAPPING.get(element)
            if uiElement:
                # TODO: validation: Check whether setText is a method? Use try
                # except maybe? Or just check and log it?
                signal.connect(uiElement.setText)

    def connect_fileinformation(self, sigFilename, sigDate, sigTime):
        # TODO: docstring, also add to class methods
        sigFilename.connect(self.toutFilename.setText)
        sigDate.connect(self.toutDate.setText)
        sigTime.connect(self.toutTime.setText)


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
                    fit = Fitting(fitConfig.config)
                    fitDict[file] = fit.currentName

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


    def add_information(self, entry:str):
        self.listInformation.addItem(entry)


    def clear_information(self):
        self.listInformation.clear()


    def get_basic_setting(self)->BasicSetting:

        grating = self.get_grating()
        fitting = self.currentFitting
        setting = BasicSetting(self.wavelength, grating, fitting)

        return setting;


    def get_grating(self)->int:
        """
        Gets the value of the ui element.

        Returns
        -------
        grating: int
            The current text of the input ui element.

        """
        # TODO: see above. compare self.wavelength
        grating = None
        try:
            grating = self.ddGrating.currentText()
            grating = int(grating)
        except:
            self.logger.error("Could not get valid value for grating!")
        return grating


    def get_raw_plot(self):
        """
        Gets the ui element.

        Returns
        -------
        MatplotlibWidget
            The ui element for plotting the raw data.

        """
        return self.mplRaw


    def get_processed_plot(self):
        """
        Gets the ui element.

        Returns
        -------
        MatplotlibWidget
            The ui element for plotting the processed data.

        """
        return self.mplProcessed