#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# third-party libs
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from PyQt5.QtCore import QSize

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT\
                                            as NavigationToolbar
from matplotlib.figure import Figure

from matplotlib import rcParams, use, pyplot
rcParams['font.size'] = 9


class MplCanvas(Canvas):
    def __init__(self, parent=None, title=' ', xlabel='x', ylabel='y',
                 xlim=None, ylim=None, xscale='linear', yscale='linear',
                 width=2, height=2, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(1, 1, 1)
        # set title and label
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        # scaling of the axes
        if xscale is not None:
            self.axes.set_xscale(xscale)
        if yscale is not None:
            self.axes.set_yscale(yscale)
        # limits of the axes
        if xlim is not None:
            self.axes.set_xlim(*xlim)
        if ylim is not None:
            self.axes.set_ylim(*ylim)

        Canvas.__init__(self, self.figure)
        self.setParent(parent)
        Canvas.setSizePolicy(self, QSizePolicy.Expanding,
                             QSizePolicy.Expanding)
        Canvas.updateGeometry(self)
        self.figure.set_tight_layout(True)

    def sizeHint(self):
        width, height = self.get_width_height()
        return QSize(width, height)

    def minimumSizeHint(self):
        return QSize(10, 10)


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None, title=' ', xlabel='x', ylabel='y',
                 xlim=None, ylim=None, xscale='linear', yscale='linear',
                 width=2, height=2, dpi=100):
        QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.axes = self.canvas.axes
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.vbl.addWidget(self.mpl_toolbar)
        self.setLayout(self.vbl)

    def draw(self):
        self.canvas.draw()