#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# third-party libs
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from PyQt5.QtCore import QSize

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT\
                                            as NavigationToolbar
from matplotlib.figure import Figure

from matplotlib import rc
from ConfigLoader import ConfigLoader


config = ConfigLoader();
PLOT = config.PLOT

# set default rc parameter.
if not PLOT == None:
    rc('lines', linewidth=PLOT.get("DEF_LINEWIDTH"),
       color=PLOT.get("DEF_AXIS_COLOR"))
    # config param?
    rc('font', size=9)

    rc("date.autoformatter", minute="%H:%M")


class MplCanvas(Canvas):
    def __init__(self, parent=None, width=2, height=2, dpi=100):
        # set up a figure
        figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = figure.add_subplot(1, 1, 1)
        Canvas.__init__(self, figure)

        # Enable methods to both axes and ui element.
        try:
            self.axes.update_layout = parent.update_layout
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


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        # init the inherited class.
        QWidget.__init__(self, parent)
        # Using a vertical layout: toolbar below graph.
        self.vbl = QVBoxLayout()
        self.add_canvas(self.vbl)
        self.add_toolbar(self.vbl)
        self.setLayout(self.vbl)


    def update_layout(self, title=None, xLabel=None, yLabel=None, xLimit=None,
                      yLimit=None):

        axes = self.axes;

        if not title == None:
            axes.set_title(title)
        if not xLabel == None:
            axes.set_xlabel(xLabel)
        if not yLabel == None:
            axes.set_ylabel(yLabel)
        if not xLimit == None:
            axes.set_xlim(*xLimit)
        if not yLimit == None:
            axes.set_ylim(*yLimit)


    def draw(self):
        # update the plot and redraw it immediately
        self.axes.legend();
        self.canvas.draw()
        self.canvas.flush_events()


    def add_canvas(self, layout, **kwargs):
        # set up the canvas object (with no parameter).
        # A canvas is a container holding several drawing elements(like axis,
        # lines, shapes, ...)
        self.canvas = MplCanvas(parent=self, **kwargs)
        self.axes = self.canvas.axes
        layout.addWidget(self.canvas)


    def add_toolbar(self, layout):
        # set up a toolbar
        mpl_toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(mpl_toolbar)
