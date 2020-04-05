#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:00:10 2020
"""


__author__ = "Hauke Wernecke"
__copyright__ = "Copyright 2020"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Hauke Wernecke/Peter Knittel"
__email__ = "hauke.wernecke@iaf.fraunhhofer.de, peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"



# local modules/libs
from ui.ui_batch_dialog import Ui_batch

class UIBatch(Ui_batch):
    """used to extend the normal class, which is generated by qt designer.
    Methods can be added (like set_all) or connections etc can be made without
    handling the normal generated class, which is overridden whenever the gui
    is changed"""
    def __init__(self, parent):
        self.parent = parent
        self.setupUi(self.parent)
        # Setup Events
        self.set_connections()


    def set_connections(self):
        """set the connections (functions/methods which are executed when
        something is clicked/..."""
        # Properties
        self.cbUpdatePlots.stateChanged.connect(self.set_prop_updatePlots)
        # TODO: what is that one good for?
        self.listFiles.setModel(self.parent.model)
        # click/valueChanged connections
        self.listFiles.clicked.connect(self.parent.open_indexed_file)
        self.btnSetFilename.clicked.connect(self.parent.set_filename)
        self.btnBrowse.clicked.connect(self.parent.browse_spectra)
        self.btnClear.clicked.connect(self.parent.clear)
        self.btnCalculate.clicked.connect(self.parent.multi_calc)
        self.btnSelectAll.clicked.connect(self.set_all)
        # update the UI whenever a parameter button is toggled/clicked
        for btn in self.BtnParameters.buttons():
            btn.toggled.connect(self.parent.update_UI)


    def set_all(self):
        """set all buttons in the group, independent if more buttons are
        added or some are deleted"""
        for button in self.BtnParameters.buttons():
            button.setChecked(True)
            
    def set_prop_updatePlots(self, enable):
        self.parent.updatePlots = enable
