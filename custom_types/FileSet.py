#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Created on Thu May  7 14:40:11 2020

@author: Hauke Wernecke
"""

# standard libs

# third-party libs

# local modules/libs
import modules.Universal as uni

# Enums

class FileSet(set):
    """
    Extends a set for interaction with a listWidget.

    Usage:
        from custum_types.FileSet import FileSet
        further usage such as a set. Additionaly one can get items of this set.

    """

    @property
    def selected_row(self):
        row = self.listWidget.currentRow()
        return row

    @selected_row.setter
    def selected_row(self, i):
        self.listWidget.setCurrentRow(i)


    def __init__(self, listWidget, iterable=()):
        """

        Parameters
        ----------
        listWidget : QListWidgetItem
            The ui element in which to display the list.
        iterable : iterable, optional
            The initial set. The default is ().
        updateOnChange : function/method, optional
            The function is called when the set was changed. The default is None.
        """
        super().__init__(iterable)
        self.listWidget = listWidget


    def __getitem__(self, i):
        """Gets the i-th item of the unsorted list."""
        if i < 0:
            raise IndexError
        files = self.to_list()
        return files[i]


    def clear(self):
        """Clears the set AND updates the ui."""
        super().clear()
        self.update_ui()


    def update(self, s):
        """Updates the set AND updates the ui."""

        # Get the current selection.
        filename = None
        index = self.selected_row
        if index >= 0:
            filename = self[index]
            index = None

        # Updates the set as usual and refresh ui.
        super().update(s)
        self.update_ui(index=index, filename=filename)


    def remove(self, t):
        """Removes an item AND updates the ui."""
        super().remove(t)
        idx = self.selected_row - 1
        self.update_ui(index=idx)


    def difference_update(self, interables):
        """Removes an item AND updates the ui."""
        super().difference_update(interables)
        self.update_ui(index=0)


    def to_list(self, naturalSort=True, indexed=False):
        """Convert the set to a sorted/indexed list."""
        files = list(self)
        if naturalSort:
            files.sort(key=uni.natural_keys)

        if indexed:
            files = uni.add_index_to_text(uni.reduce_path(files))

        return files


    def update_ui(self, index=None, filename=None):
        """Update ui with converted and sorted/indexed list."""
        files = self.to_list(indexed=True)

        self.listWidget.clear()
        self.listWidget.addItems(files)

        if not index is None:
            # max(index, 0) ensures that no row with a neg. index is selected.
            self.selected_row = max(index, 0)
        elif not filename is None:
            self.select_row_by_filename(filename)


    def select_row_by_filename(self, filename):
        """Gets the i-th item of the sorted list by the filename."""
        files = self.to_list()
        i = files.index(filename)
        self.selected_row = i