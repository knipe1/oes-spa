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
from modules.filehandling.filereading.filereader import FileReader
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

    box.batchFile = filename
    # box.mplRaw.axes.plot(np.arange(10), np.random.normal(1, size=10))
    # box.mplRaw.draw()




    box._window.btnAddBatchfile.click()
    box._window.btnAddBatchfile.click()

    def read_batch():
        box._window.batchlist.topLevelItem(0).get_values_from_child(0)
        # for i in range(3):
        #     item = box.batchlist.currentItem()
        #     print(i, item.text(i), )

        #     try:
        #         print(box.batchlist.itemWidget(item, i).currentText())
        #     except Exception:
        #         pass

    box._window.batchlist.clicked.connect(read_batch)



    # box.plot_trace_from_batchfile("/home/hauke/IAF/oes-spectra-analysis-Homeversion/_batch.ba", "Peak height", "Example Peak")

    # Omitting show() will lead to a hidden application -> Most often not what you want.
    main_window.show()

    sys.exit(app.exec_())




# Run as main if executed and not included
main()
