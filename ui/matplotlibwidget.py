#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# standard libs
import matplotlib.pyplot as mpl

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as Toolbar

# third-party libs
from PyQt5.QtWidgets import QWidget, QVBoxLayout

# local modules/libs
from loader.ConfigLoader import ConfigLoader

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


    def update_layout(self, xLabel=None, yLabel=None, xLimit=None)->None:
        """Updates the general layout with (optional) properties."""

        axes = self.axes

        if xLabel:
            axes.set_xlabel(xLabel)
        if yLabel:
            axes.set_ylabel(yLabel)

        if xLimit:
            axes.set_xlim(*xLimit)





class MatplotlibWidget(QWidget):
    def __init__(self, parent=None)->None:
        super().__init__()
        self.vbl = QVBoxLayout()
        self.add_canvas()
        self.add_toolbar()
        self.setLayout(self.vbl)


    def draw(self)->None:
        """Draw the plot immediately."""
        if self.axes.get_legend_handles_labels()[0]:
            self.axes.legend()

        self.center_plot()
        self.canvas.draw()

        # Refactored - events were flushed in BatchAnalysis also allow to
        # cancel the analysis. Therefore, the next line is not needed anymore.
        # self.canvas.flush_events()


    def center_plot(self)->None:
        """Center the plot to the current data."""
        xData = self.axes.lines[-1].get_xdata()
        left = xData[0]
        right = xData[-1]
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
