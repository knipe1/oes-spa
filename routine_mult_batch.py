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


# class combocompanies(QComboBox):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.addItems(["Microsoft", "Apple", "Boron"])

#     def getComboValue(self):
#         print(self.currentText())
#         # return self.currentText()





def main():
    """Main program """
    filename = "./_batch.ba"
    # batchfile = FileReader("./_batch.ba")


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
        for i in range(3):
            item = box.batchlist.currentItem()
            print(i, item.text(i), )

            try:
                print(box.batchlist.itemWidget(item, i).currentText())
            except Exception:
                pass

    box._window.batchlist.currentItemChanged.connect(read_batch)
    print(box._window.batchlist.get_batchfiles())

    # Custom code
    # class DelegateItem(QStyledItemDelegate):
    #     pass

    # item1 = DelegateItem(box.treeWidget)
    # box.treeWidget.setItemDelegate(item1)




    # Omitting show() will lead to a hidden application -> Most often not what you want.
    main_window.show()

    sys.exit(app.exec_())




# Run as main if executed and not included
main()
