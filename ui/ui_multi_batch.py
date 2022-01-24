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
        Form.resize(1000, 930)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.foutBatchfile = QtWidgets.QLineEdit(Form)
        self.foutBatchfile.setObjectName("foutBatchfile")
        self.horizontalLayout.addWidget(self.foutBatchfile)
        self.btnSelectBatchfile = QtWidgets.QPushButton(Form)
        self.btnSelectBatchfile.setObjectName("btnSelectBatchfile")
        self.horizontalLayout.addWidget(self.btnSelectBatchfile)
        self.btnAddBatchfile = QtWidgets.QPushButton(Form)
        self.btnAddBatchfile.setObjectName("btnAddBatchfile")
        self.horizontalLayout.addWidget(self.btnAddBatchfile)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.batchlist = TreeWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.batchlist.sizePolicy().hasHeightForWidth())
        self.batchlist.setSizePolicy(sizePolicy)
        self.batchlist.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.batchlist.setAlternatingRowColors(True)
        self.batchlist.setIndentation(10)
        self.batchlist.setObjectName("batchlist")
        self.batchlist.header().setDefaultSectionSize(100)
        self.batchlist.header().setMinimumSectionSize(30)
        self.batchlist.header().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.batchlist)
        self.mplBatch = MatplotlibWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.mplBatch.sizePolicy().hasHeightForWidth())
        self.mplBatch.setSizePolicy(sizePolicy)
        self.mplBatch.setObjectName("mplBatch")
        self.verticalLayout.addWidget(self.mplBatch)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.btnSelectBatchfile.setText(_translate("Form", "Select Batchfile"))
        self.btnAddBatchfile.setText(_translate("Form", "Add"))
        self.batchlist.setSortingEnabled(True)
        self.batchlist.headerItem().setText(0, _translate("Form", "Filename"))
        self.batchlist.headerItem().setText(1, _translate("Form", "Peak Name"))
        self.batchlist.headerItem().setText(2, _translate("Form", "Characteristic"))
        self.batchlist.headerItem().setText(3, _translate("Form", "X-Offset"))
        self.batchlist.headerItem().setText(4, _translate("Form", "Y-Offset"))
        self.batchlist.headerItem().setText(5, _translate("Form", "Deletion"))

from ui.matplotlibwidget import MatplotlibWidget
from ui.treewidget import TreeWidget
