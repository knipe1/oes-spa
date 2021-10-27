# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'multi_batch.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(739, 707)
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(-1, 14, 741, 691))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.mplRaw = MatplotlibWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplRaw.sizePolicy().hasHeightForWidth())
        self.mplRaw.setSizePolicy(sizePolicy)
        self.mplRaw.setMinimumSize(QtCore.QSize(400, 200))
        self.mplRaw.setMaximumSize(QtCore.QSize(900, 600))
        self.mplRaw.setObjectName("mplRaw")
        self.gridLayout.addWidget(self.mplRaw, 2, 0, 1, 3)
        self.foutBatchfile = QtWidgets.QLineEdit(self.widget)
        self.foutBatchfile.setObjectName("foutBatchfile")
        self.gridLayout.addWidget(self.foutBatchfile, 0, 1, 1, 1)
        self.btnAddBatchfile = QtWidgets.QPushButton(self.widget)
        self.btnAddBatchfile.setObjectName("btnAddBatchfile")
        self.gridLayout.addWidget(self.btnAddBatchfile, 0, 2, 1, 1)
        self.btnSelectBatchfile = QtWidgets.QPushButton(self.widget)
        self.btnSelectBatchfile.setObjectName("btnSelectBatchfile")
        self.gridLayout.addWidget(self.btnSelectBatchfile, 0, 0, 1, 1)
        self.batchlist = TreeWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.batchlist.sizePolicy().hasHeightForWidth())
        self.batchlist.setSizePolicy(sizePolicy)
        self.batchlist.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed|QtWidgets.QAbstractItemView.SelectedClicked)
        self.batchlist.setAlternatingRowColors(True)
        self.batchlist.setIndentation(15)
        self.batchlist.setObjectName("batchlist")
        self.batchlist.header().setDefaultSectionSize(120)
        self.gridLayout.addWidget(self.batchlist, 1, 0, 1, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.btnAddBatchfile.setText(_translate("Form", "Add"))
        self.btnSelectBatchfile.setText(_translate("Form", "Select Batchfile"))
        self.batchlist.setSortingEnabled(True)
        self.batchlist.headerItem().setText(0, _translate("Form", "Filename"))
        self.batchlist.headerItem().setText(1, _translate("Form", "Peak-Name"))
        self.batchlist.headerItem().setText(2, _translate("Form", "Characteristic"))
        self.batchlist.headerItem().setText(3, _translate("Form", "X-Offset"))
        self.batchlist.headerItem().setText(4, _translate("Form", "Y-Offset"))

from ui.matplotlibwidget import MatplotlibWidget
from ui.treewidget import TreeWidget
