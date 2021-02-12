#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 12:17:47 2021

@author: hauke
"""


# standard libs

# third-party libs
from PyQt5.QtWidgets import QListWidget

# local modules/libs
from loader.ConfigLoader import ConfigLoader
import modules.Universal as uni


BATCH = ConfigLoader().BATCH


class IndexedListWidget(QListWidget):

    def setItems(self, labels:list)->None:
        """Resets the items and sets the labels as new list."""
        self.clear()
        reducedLabels = uni.reduce_paths(labels)
        formatLabels = self.add_index_to_text(reducedLabels)
        super().addItems(formatLabels)


    @staticmethod
    def add_index_to_text(texts:list)->str:
        """
        Adding the index of a list item in front of the item.
        May the 44th item be "File", then the returning element would be "  44:File"

        Parameters
        ----------
        texts : list of strings

        Returns
        -------
        yield: the text with the index prior

        """
        sep = BATCH["SEPARATOR"]
        for idx, text in enumerate(texts):
            index = format(idx + 1, BATCH["INDEX_FORMAT"])
            yield index + sep + text
