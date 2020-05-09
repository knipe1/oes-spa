#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  7 14:40:11 2020

@author: hauke
"""

# local modules/libs
import modules.Universal as uni

class FileSet(set):
    """
    Extends a set with interaction with a listWidget.

    Usage:
        from custum_types.FileSet import FileSet
        further usage such as a set. And one can also get an item of this set.


    Attributes
    ----------
    listWidget : QListWidgetItem
        The widget which displays the set/list.



    Methods
    -------
    to_list():
        Convert the set to a sorted/indexed list.
    update_ui():
        Update ui with converted and sorted/indexed list.
    has_listWidget():
        Checks the object for a list widget attribute.

    """


    def __init__(self, iterable=(), listWidget=None, updateOnChange=None):
        """
        Init the Object.

        Parameters
        ----------
        iterable : iterable, optional
            The initial set. The default is ().
        listWidget : QListWidgetItem, optional
            The ui element in which to display the list. The default is None.
        updateOnChange : function/method, optional
            The function is called when the set was changed. The default is
            None.
        """
        super().__init__(iterable)
        self.listWidget = listWidget
        # Workaround: It's not possible to emit a signal like viewChanged,
        # therefore the function is provided.
        self.updateOnChange = updateOnChange


    def __getitem__(self, i):
        """Gets the i-th item of the sorted list."""
        files = self.to_list()
        return list.__getitem__(files, i)


    def clear(self):
        """Clears the set AND updates the ui."""
        super().clear()
        self.update_ui()


    def update(self, s):
        """Updates the set AND updates the ui."""

        # Get the current selection.
        if self.has_listWidget():
            selectedIdx = self.listWidget.currentRow()
            if selectedIdx >= 0:
                filename = self[selectedIdx]

        # Updates the set as usual and refresh ui.
        super().update(s)
        self.update_ui()

        # Select the first or previously selected file.
        if (not selectedIdx is None) and selectedIdx < 0 :
            self.listWidget.setCurrentRow(0)
        else:
            self.selectRowByFilename(filename)

    def remove(self, t):
        """Removes an item AND updates the ui."""
        super().remove(t)
        self.update_ui()


    def to_list(self, naturalSort=True, indexed=False):
        """Convert the set to a sorted/indexed list."""
        files = list(self)
        if naturalSort:
            files.sort(key=uni.natural_keys)
        if indexed:
            files = uni.add_index_to_text(uni.reduce_path(files))
        return files


    def update_ui(self):
        """Update ui with converted and sorted/indexed list."""
        if self.has_listWidget():
            files = self.to_list(indexed=True)

            self.listWidget.clear()
            self.listWidget.addItems(files)

        if self.updateOnChange:
            self.updateOnChange()


    def selectRowByFilename(self, filename):
        """Gets the i-th item of the sorted list."""
        files = self.to_list()
        i = files.index(filename)
        if self.has_listWidget():
            self.listWidget.setCurrentRow(i)


    def has_listWidget(self):
        """Checks the object for a list widget attribute."""
        return not (self.listWidget is None)