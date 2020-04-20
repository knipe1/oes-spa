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
import modules.Universal as uni
from ui.ui_main_window import Ui_main
from Logger import Logger

# enums
from custom_types.UI_RESULTS import UI_RESULTS

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
    connect_exportRaw(fun):
        Interface to connect fun to triggered signal of the button.
    connect_exportProcessed(fun):
        Interface to connect fun to triggered signal of the button.
    connect_showBatch(fun):
        Interface to connect fun to triggered signal of the button.
    connect_openFile(fun):
        Interface to connect fun signal of the button and action.
    connect_selectFitting(fun):
        Interface to connect fun to text changed signal of the dropdown.
    ConnectSlotResults(signals:dict):
        Connect given signals to corresponding ui elements.
    """

    # set up the logger
    logger = Logger(__name__)

    # Getting the neccessary configs
    config = uni.load_config()
    FITTING = config["FITTING"];

    ### properties

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

        if not uiElement == None:
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
        self.__post_init__()


    def __post_init__(self):
        self.UI_MAPPING = self.init_mapping()
        self.fittings = self.retrieve_fittings()


    # TODO: ought be immutable
    # TODO: import from somewhere? Issue: can't link to ui element
    def init_mapping(self):
        mapping = {"fitting": self.ddFitting,
                   UI_RESULTS.tout_PEAK_HEIGHT: self.toutPeakHeight,
                   UI_RESULTS.tout_PEAK_AREA: self.toutPeakArea,
                   UI_RESULTS.tout_BASELINE: self.toutBaseline,
                   }
        return mapping


    # Connect methods: Provides at least one event (signal) to connect to a
    # function
    # act: option in a dropdown of the menu bar
    # btn : Button
    def connect_exportRaw(self, fun):
        """Interface to connect fun to triggered signal of the button."""
        self.actSaveRaw.triggered.connect(fun)


    def connect_exportProcessed(self, fun):
        """Interface to connect fun to triggered signal of the button."""
        self.actSaveProcessed.triggered.connect(fun)


    def connect_showBatch(self, fun):
        """Interface to connect fun to triggered signal of the button."""
        self.actOpenBatch.triggered.connect(fun)


    def connect_openFile(self, fun):
        """Interface to connect fun signal of the button and action."""
        self.btnFileOpen.clicked.connect(fun)
        self.actOpen.triggered.connect(fun)


    def connect_selectFitting(self, fun):
        """Interface to connect fun to text changed signal of the dropdown."""
        # TODO: evaluate the pro and cons
        # Pro: ui element can be changed in one position
        # Pro/Con: ErrorHandling. Should throw an Error if there is no
        # attribute ddFitting
        # Con: Readability
        # Alternatives:
        # self.ddFitting.currentTextChanged.connect(fun)
        # self.UI_MAPPING.get("fitting").currentTextChanged.connect(fun)
        uiElement = self.UI_MAPPING.get("fitting")
        uiElement.currentTextChanged.connect(fun)
        # Emit the signal once to trigger the connected methods once.
        uiElement.currentTextChanged.emit(uiElement.currentText())



    def ConnectSlotResults(self, signals:dict):
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
            self.logger.warning("ConnectSlotResults: No dict given")
            return False

        # connect the signal with the corresponding ui element
        for element, signal in signals.items():
            # skip signal if not qt-signal
            if not isinstance(signal, pyqtBoundSignal):
                self.logger.info("ConnectSlotResults: No valid signal")
                continue
            # skip key if not defined in enum
            if not isinstance(element, UI_RESULTS):
                self.logger.info("ConnectSlotResults: No valid element")
                continue

            # if a ui element is linked to that element, the signal is
            # connected
            uiElement = self.UI_MAPPING.get(element)
            if uiElement:
                # TODO: validation: Check whether setText is a method? Use try
                # except maybe? Or just check and log it?
                signal.connect(uiElement.setText)


    def retrieve_fittings(self) -> list:
        """
        Retrieve all fitting files of the directory of fittings.

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
                    fitConfig = uni.load_config(path)
                    fitName = fitConfig.get("NAME")
                    fitDict[file] = fitName

        return fitDict