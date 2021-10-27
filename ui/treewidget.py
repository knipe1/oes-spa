#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 12:08:27 2021

@author: hauke
"""

from PyQt5.QtWidgets import QTreeWidget





class TreeWidget(QTreeWidget):

    def get_batchfiles(self):
        root = self.invisibleRootItem()
        toplevelItemCount = root.childCount()
        return [root.child(i).filename for i in range(toplevelItemCount)]
