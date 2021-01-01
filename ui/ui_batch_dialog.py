# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_batch(object):
    def setupUi(self, batch):
        batch.setObjectName("batch")
        batch.resize(638, 850)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(batch.sizePolicy().hasHeightForWidth())
        batch.setSizePolicy(sizePolicy)
        batch.setAcceptDrops(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("afm.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        batch.setWindowIcon(icon)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(batch)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.layoutCSVFile = QtWidgets.QHBoxLayout()
        self.layoutCSVFile.setObjectName("layoutCSVFile")
        self.foutBatchfile = QtWidgets.QLineEdit(batch)
        self.foutBatchfile.setReadOnly(True)
        self.foutBatchfile.setObjectName("foutBatchfile")
        self.layoutCSVFile.addWidget(self.foutBatchfile)
        self.btnSetFilename = QtWidgets.QPushButton(batch)
        self.btnSetFilename.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSetFilename.sizePolicy().hasHeightForWidth())
        self.btnSetFilename.setSizePolicy(sizePolicy)
        self.btnSetFilename.setMinimumSize(QtCore.QSize(110, 0))
        self.btnSetFilename.setObjectName("btnSetFilename")
        self.layoutCSVFile.addWidget(self.btnSetFilename)
        self.verticalLayout_2.addLayout(self.layoutCSVFile)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.foutWatchdog = QtWidgets.QLineEdit(batch)
        self.foutWatchdog.setReadOnly(True)
        self.foutWatchdog.setObjectName("foutWatchdog")
        self.horizontalLayout.addWidget(self.foutWatchdog)
        self.btnWatchdog = QtWidgets.QPushButton(batch)
        self.btnWatchdog.setCheckable(True)
        self.btnWatchdog.setChecked(False)
        self.btnWatchdog.setDefault(False)
        self.btnWatchdog.setFlat(False)
        self.btnWatchdog.setObjectName("btnWatchdog")
        self.horizontalLayout.addWidget(self.btnWatchdog)
        self.btnSetWatchdogDir = QtWidgets.QPushButton(batch)
        self.btnSetWatchdogDir.setMinimumSize(QtCore.QSize(110, 0))
        self.btnSetWatchdogDir.setObjectName("btnSetWatchdogDir")
        self.horizontalLayout.addWidget(self.btnSetWatchdogDir)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.listFiles = QtWidgets.QListWidget(batch)
        self.listFiles.setMaximumSize(QtCore.QSize(800, 500))
        self.listFiles.setAcceptDrops(True)
        self.listFiles.setObjectName("listFiles")
        self.horizontalLayout_2.addWidget(self.listFiles)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnBrowse = QtWidgets.QPushButton(batch)
        self.btnBrowse.setEnabled(True)
        self.btnBrowse.setMinimumSize(QtCore.QSize(110, 0))
        self.btnBrowse.setObjectName("btnBrowse")
        self.verticalLayout.addWidget(self.btnBrowse)
        self.btnClear = QtWidgets.QPushButton(batch)
        self.btnClear.setEnabled(True)
        self.btnClear.setObjectName("btnClear")
        self.BtnFileaction = QtWidgets.QButtonGroup(batch)
        self.BtnFileaction.setObjectName("BtnFileaction")
        self.BtnFileaction.setExclusive(False)
        self.BtnFileaction.addButton(self.btnClear)
        self.verticalLayout.addWidget(self.btnClear)
        spacerItem = QtWidgets.QSpacerItem(20, 255, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.layoutProcess = QtWidgets.QHBoxLayout()
        self.layoutProcess.setObjectName("layoutProcess")
        self.barProgress = QtWidgets.QProgressBar(batch)
        self.barProgress.setProperty("value", 0)
        self.barProgress.setObjectName("barProgress")
        self.layoutProcess.addWidget(self.barProgress)
        self.radTrace = QtWidgets.QRadioButton(batch)
        self.radTrace.setObjectName("radTrace")
        self.RadProcess = QtWidgets.QButtonGroup(batch)
        self.RadProcess.setObjectName("RadProcess")
        self.RadProcess.addButton(self.radTrace)
        self.layoutProcess.addWidget(self.radTrace)
        self.radSpectra = QtWidgets.QRadioButton(batch)
        self.radSpectra.setEnabled(True)
        self.radSpectra.setObjectName("radSpectra")
        self.RadProcess.addButton(self.radSpectra)
        self.layoutProcess.addWidget(self.radSpectra)
        self.radExport = QtWidgets.QRadioButton(batch)
        self.radExport.setChecked(True)
        self.radExport.setObjectName("radExport")
        self.RadProcess.addButton(self.radExport)
        self.layoutProcess.addWidget(self.radExport)
        self.btnAnalyze = QtWidgets.QPushButton(batch)
        self.btnAnalyze.setEnabled(False)
        self.btnAnalyze.setObjectName("btnAnalyze")
        self.BtnFileaction.addButton(self.btnAnalyze)
        self.layoutProcess.addWidget(self.btnAnalyze)
        self.btnCancel = QtWidgets.QPushButton(batch)
        self.btnCancel.setObjectName("btnCancel")
        self.layoutProcess.addWidget(self.btnCancel)
        self.verticalLayout_2.addLayout(self.layoutProcess)
        self.boxTrace = QtWidgets.QGroupBox(batch)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boxTrace.sizePolicy().hasHeightForWidth())
        self.boxTrace.setSizePolicy(sizePolicy)
        self.boxTrace.setMinimumSize(QtCore.QSize(310, 330))
        self.boxTrace.setObjectName("boxTrace")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.boxTrace)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.boxTrace)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.cmbTrace = QtWidgets.QComboBox(self.boxTrace)
        self.cmbTrace.setObjectName("cmbTrace")
        self.gridLayout_2.addWidget(self.cmbTrace, 0, 1, 1, 1)
        self.btnImport = QtWidgets.QPushButton(self.boxTrace)
        self.btnImport.setObjectName("btnImport")
        self.gridLayout_2.addWidget(self.btnImport, 0, 2, 1, 1)
        self.mplTrace = MatplotlibWidget(self.boxTrace)
        self.mplTrace.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplTrace.sizePolicy().hasHeightForWidth())
        self.mplTrace.setSizePolicy(sizePolicy)
        self.mplTrace.setMinimumSize(QtCore.QSize(370, 330))
        self.mplTrace.setMaximumSize(QtCore.QSize(800, 800))
        self.mplTrace.setBaseSize(QtCore.QSize(100, 100))
        self.mplTrace.setAutoFillBackground(False)
        self.mplTrace.setObjectName("mplTrace")
        self.gridLayout_2.addWidget(self.mplTrace, 1, 0, 1, 3)
        self.verticalLayout_2.addWidget(self.boxTrace)

        self.retranslateUi(batch)
        QtCore.QMetaObject.connectSlotsByName(batch)
        batch.setTabOrder(self.btnSetFilename, self.btnBrowse)
        batch.setTabOrder(self.btnBrowse, self.foutBatchfile)
        batch.setTabOrder(self.foutBatchfile, self.listFiles)
        batch.setTabOrder(self.listFiles, self.btnClear)

    def retranslateUi(self, batch):
        _translate = QtCore.QCoreApplication.translate
        batch.setWindowTitle(_translate("batch", "Batch Analysis"))
        self.btnSetFilename.setText(_translate("batch", "&Set Filename"))
        self.btnWatchdog.setText(_translate("batch", "Active Watchdog"))
        self.btnSetWatchdogDir.setText(_translate("batch", "Set Directory"))
        self.btnBrowse.setText(_translate("batch", "&Browse Files"))
        self.btnClear.setText(_translate("batch", "Clear"))
        self.radTrace.setText(_translate("batch", "Plot Trace"))
        self.radSpectra.setText(_translate("batch", "Plot Spectra"))
        self.radExport.setText(_translate("batch", "Export"))
        self.btnAnalyze.setText(_translate("batch", "&Analyze"))
        self.btnCancel.setText(_translate("batch", "Cancel"))
        self.label.setText(_translate("batch", "Select characteristic:"))
        self.btnImport.setText(_translate("batch", "Import Trace"))

from ui.matplotlibwidget import MatplotlibWidget
