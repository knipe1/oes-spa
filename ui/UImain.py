# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 2020
"""


__author__ = "Hauke Wernecke"
__copyright__ = "Copyright 2020"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Hauke Wernecke/Peter Knittel"
__email__ = "hauke.wernecke@iaf.fraunhhofer.de, peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"


from ui.ui_main_window import Ui_main

class UImain(Ui_main):
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
        # Action: option in a dropdown of the menu bar
        # Bt : Button
        self.BtFileOpen.clicked.connect(self.parent.file_open)
        self.ActionOpen.triggered.connect(self.parent.file_open)
        self.BtRedraw.clicked.connect(self.parent.redraw)
        self.ActionRedraw.triggered.connect(self.parent.redraw)
        self.ActionSaveRaw.triggered.connect(self.parent.save_raw)
        self.ActionSaveProcessed.triggered.connect(self.parent.save_processed)
        self.ActionAnalyzeMultipleFiles.triggered.\
            connect(self.parent.batch.show)