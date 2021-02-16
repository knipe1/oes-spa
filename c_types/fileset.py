#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
class: FileSet

@author: Hauke Wernecke
"""

# standard libs

# third-party libs
from dependencies.natsort.natsort import natsorted

# local modules/libs
import modules.universal as uni

# Enums

class FileSet(set):
    """
    Extends a set for interaction with a listWidget.

    Usage:
        from custum_types.fileset import FileSet
        further usage such as a set. Additionaly one can get items of this set.

    """

    @property
    def current_row(self)->str:
        return self._listWidget.currentRow()

    @current_row.setter
    def current_row(self, i:int)->None:
        self._listWidget.setCurrentRow(i)


    def __init__(self, listWidget, iterable=())->None:
        """

        Parameters
        ----------
        listWidget : QListWidgetItem
            The ui element in which to display the list.
        iterable : iterable, optional
            The initial set. The default is ().
        """
        super().__init__(iterable)
        self._listWidget = listWidget


    def __getitem__(self, i:int)->str:
        """Gets the i-th item of the unsorted list."""
        if i < 0:
            raise IndexError
        files = self.to_list()
        return files[i]


    def clear(self)->None:
        """Clears the set AND updates the ui."""
        super().clear()
        self._listWidget.clear()


    def update(self, files:set, noSelection:bool=False)->None:
        """Updates the set AND updates the ui."""
        filename = None
        index = self.current_row
        if not noSelection and index >= 0:
            filename = self[index]

        files = self.validate(files)
        super().update(files)
        self.update_ui(filename=filename)


    def validate(self, files:set):
        for file in files:
            if not uni.is_valid_suffix(file):
                files.remove(file)
        return files



    def remove(self, t:str)->None:
        """Removes an item AND updates the ui."""
        super().remove(t)
        # max ensures that no neg. index is selected.
        idx = max(self.current_row - 1, 0)
        self.update_ui(index=idx)


    def difference_update(self, iterables:set)->None:
        """Removes an item AND updates the ui."""
        super().difference_update(iterables)
        self.update_ui()


    def to_list(self)->None:
        """Convert the set to a sorted list."""
        files = natsorted(self)
        return files


    def update_ui(self, index:int=None, filename:str=None)->None:
        """Update ui with converted and sorted/indexed list."""
        self._listWidget.setItems(self.to_list())
        if index is not None:
            self.current_row = index
        elif filename is not None:
            self.select_row_by_filename(filename)


    def select_row_by_filename(self, filename:str)->None:
        """Gets the i-th item of the sorted list by the filename."""
        files = self.to_list()
        i = files.index(filename)
        self.current_row = i
