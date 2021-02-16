#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# standard libs
import matplotlib.pyplot as mpl
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as Toolbar

# third-party libs
from PyQt5.QtWidgets import QWidget, QVBoxLayout

# local modules/libs
from loader.configloader import ConfigLoader

PLOT = ConfigLoader().PLOT


# set default rc parameter.
if PLOT:
    mpl.rc('lines', linewidth=PLOT.get("DEF_LINEWIDTH"),
                    color=PLOT.get("DEF_AXIS_COLOR"))
    mpl.rc('font', size=9)
    # Formats the axis if data are dates.
    mpl.rc("date.autoformatter", minute="%H:%M")


class MplCanvas(Canvas):
    def __init__(self, dpi=100)->None:
        # Init a figure before init super, because figure is a arg of super.
        self.figure = mpl.Figure(dpi=dpi)
        self.axes = self.figure.add_subplot()
        super().__init__(self.figure)

        # Improves the layout and look of the plots.
        self.figure.set_tight_layout(True)

        # Enable methods to both axes and ui element.
        try:
            self.axes.update_layout = self.update_layout
        except AttributeError as err:
            print(err)


    def update_layout(self, xLabel=None, yLabel=None)->None:
        """Updates the general layout with (optional) properties."""
        if xLabel:
            self.axes.set_xlabel(xLabel)
        if yLabel:
            self.axes.set_ylabel(yLabel)





class MatplotlibWidget(QWidget):
    def __init__(self, parent=None)->None:
        super().__init__()
        self.vbl = QVBoxLayout()
        self.add_canvas()
        self.add_toolbar()
        self.setLayout(self.vbl)


    def draw(self, zoomOn:np.ndarray=None)->None:
        """Draw the plot immediately."""
        if self.axes.get_legend_handles_labels()[0]:
            self.axes.legend()

        self.axes.relim(visible_only=True)
        self.axes.autoscale(axis="y")

        if not zoomOn is None:
            self.center_plot(zoomOn)
        self.canvas.draw()

        # Refactored - events were flushed in BatchAnalysis also allow to
        # cancel the analysis. Therefore, the next line is not needed anymore.
        # self.canvas.flush_events()


    def center_plot(self, zoomOn:np.ndarray)->None:
        """Center the plot to the current data."""
        left = zoomOn.min()
        right = zoomOn.max()
        if left < right:
            self.axes.set_xlim((left, right))


    def add_canvas(self, **kwargs)->None:
        # A canvas is a container holding several drawing elements(like axis, lines, shapes, ...)
        self.canvas = MplCanvas(**kwargs)
        self.axes = self.canvas.axes
        self.vbl.addWidget(self.canvas)


    def add_toolbar(self):
        mplToolbar = Toolbar(self.canvas, self)
        self.vbl.addWidget(mplToolbar)
