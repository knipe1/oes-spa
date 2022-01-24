#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 16:36:55 2021

@author: hauke
"""



# third-party libs
from PyQt5.QtWidgets import QTreeWidgetItem


# local modules/libs
from ui.deletebutton import DeleteButton


# enums and dataclasses


class TreeWidgetItem(QTreeWidgetItem):
    """Extens the funcionality by a delete-button."""

    def init_widgets(self, parent):
        self.add_delete_as_widget(parent)


    def add_delete_as_widget(self, parent):
        btn = DeleteButton(self.delete)
        lastColumn = parent.columnCount() - 1
        parent.setItemWidget(self, lastColumn, btn)


    def delete(self):
        pass
