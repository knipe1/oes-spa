#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 12:30:27 2021

@author: hauke
"""

# standard libs
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QTreeWidgetItem
from PyQt5.QtWidgets import QComboBox
from modules.multibatchform import MultiBatchForm

import numpy as np
from modules.filehandling.filereading.bareader import BaReader
# import dialog_messages as dialog
import modules.universal as uni


from ui.ui_multi_batch import Ui_Form



def main():
    """Main program """
    filename = "./_batch.ba"


    # Create an application in which the GUI can be displayed.
    app = QApplication(sys.argv)
    # Create a MainWindow which nest the widget (here: Ui_Form).
    main_window = QMainWindow()


    box = MultiBatchForm(main_window)

    # routine
    box.batchFile = filename
    box._window.btnAddBatchfile.click()

    # Test selection
    def read_batch():
        box._window.batchlist.topLevelItem(0).get_values_from_child(0)
    box._window.batchlist.clicked.connect(read_batch)



    box.plot_trace_from_batchfile(box._window.batchlist.get_settings())

    # Omitting show() will lead to a hidden application -> Most often not what you want.
    main_window.show()
    sys.exit(app.exec_())

# Run as main if executed and not included
main()
