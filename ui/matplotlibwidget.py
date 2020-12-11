#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# standard libs
import matplotlib.pyplot as mpl

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT\
                                            as NavigationToolbar

# third-party libs
from PyQt5.QtWidgets import QWidget, QVBoxLayout

# local modules/libs
from ConfigLoader import ConfigLoader

config = ConfigLoader();
PLOT = config.PLOT

# set default rc parameter.
if not PLOT == None:
    mpl.rc('lines',
           linewidth=PLOT.get("DEF_LINEWIDTH"),
           color=PLOT.get("DEF_AXIS_COLOR"))
    # TODO: config param?
    mpl.rc('font', size=9)
    # TODO: config param?
    # Formats the axis if data are dates.
    mpl.rc("date.autoformatter", minute="%H:%M")


class MplCanvas(Canvas):
    def __init__(self, parent=None, width=2, height=2, dpi=100):
        # Init a figure before init super, because figure is a arg of super.
        figure = mpl.Figure(figsize=(width, height), dpi=dpi)
        self.axes = figure.add_subplot(1, 1, 1)
        super(MplCanvas, self).__init__(figure)

        # Enable methods to both axes and ui element.
        try:
            self.axes.update_layout = self.update_layout
        except AttributeError as err:
            print(err)

        # TODO: neccessary?
        # self.setParent(parent)
        # TODO: neccessary?
        # docs: https://doc.qt.io/qt-5/qsizepolicy.html
        # Canvas.setSizePolicy(self, QSizePolicy.Expanding,
        #                      QSizePolicy.Expanding)
        # TODO: neccessary?
        # Canvas.updateGeometry(self)

        # Improves the layout and look of the plots.
        self.figure.set_tight_layout(True)


    def update_layout(self, title=None, xLabel=None, yLabel=None, xLimit=None,
                      yLimit=None, auto=False):
        """Updates the general layout with (optional) properties."""

        axes = self.axes;

        if not title == None:
            axes.set_title(title)

        if not xLabel == None:
            axes.set_xlabel(xLabel)
        if not yLabel == None:
            axes.set_ylabel(yLabel)

        if auto:
            axes.set_xlim(auto=True)
            axes.set_ylim(auto=True)

        if not xLimit == None:
            axes.set_xlim(*xLimit)
        if not yLimit == None:
            axes.set_ylim(*yLimit)





class MatplotlibWidget(QWidget):
    def __init__(self, parent):
        super(MatplotlibWidget, self).__init__()
        self.vbl = QVBoxLayout()
        self.add_canvas(self.vbl)
        self.add_toolbar(self.vbl)
        self.setLayout(self.vbl)


    def draw(self):
        """Draw the plot immediately."""
        if self.axes.get_legend_handles_labels()[0]:
            self.axes.legend();
        self.canvas.draw()

        # Refactored - events were flushed in BatchAnalysis also allow to
        # cancel the analysis. Therefore, the next line is not needed anymore.
        # self.canvas.flush_events()


    def add_canvas(self, layout, **kwargs):
        """Add a Canvas container to the layout."""
        # A canvas is a container holding several drawing elements(like axis,
        # lines, shapes, ...)
        self.canvas = MplCanvas(parent=self, **kwargs)
        self.axes = self.canvas.axes
        layout.addWidget(self.canvas)


    def add_toolbar(self, layout):
        """Add a toolbar to the layout."""
        # Set up a toolbar.
        mplToolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(mplToolbar)

