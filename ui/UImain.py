# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 2020
"""


__author__ = "Hauke Wernecke"
__copyright__ = "Copyright 2020"
__license__ = ""
__version__ = "a1"
__maintainer__ = "Hauke Wernecke/Peter Knittel"
__email__ = "hauke.wernecke@iaf.fraunhhofer.de", "peter.knittel@iaf.fraunhhofer.de"
__status__ = "alpha"


from ui.ui_main_window import Ui_main

class UIMain(Ui_main):
    """used to extend the normal class, which is generated by qt designer.
    Methods can be added (like set_all) or connections etc can be made without
    handling the normal generated class, which is overridden whenever the gui
    is changed"""
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
        self.parent = parent
        self.setupUi(self.parent)
        # Setup Events
        self.set_connections()


    def set_connections(self):
        """
        set the connections (functions/methods which are executed when
        something is clicked/...

        Returns
        -------
        None.

        """
        # act: option in a dropdown of the menu bar
        # btn : Button
        self.btnFileOpen.clicked.connect(self.parent.file_open)
        self.actOpen.triggered.connect(self.parent.file_open)
        self.actRedraw.triggered.connect(self.parent.redraw)
        self.actSaveRaw.triggered.connect(self.parent.save_raw)
        self.actSaveProcessed.triggered.connect(self.parent.save_processed)
        self.actOpenBatch.triggered.connect(self.parent.batch.show)