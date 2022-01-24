# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, main):
        main.setObjectName("main")
        self.centralwidget = QtWidgets.QWidget(main)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.mplRaw = MatplotlibWidget(self.gridLayout)
        self.mplRaw.setObjectName("mplRaw")
        self.gridLayout.addWidget(self.mplRaw, 1, 0, 1, 1)
        main.setCentralWidget(self.centralwidget)

from ui.matplotlibwidget import MatplotlibWidget
