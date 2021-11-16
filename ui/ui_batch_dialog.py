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
        batch.resize(956, 950)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(batch)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabs = QtWidgets.QTabWidget(batch)
        self.tabs.setObjectName("tabs")
        self.tab_single_batch = QtWidgets.QWidget()
        self.tab_single_batch.setObjectName("tab_single_batch")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_single_batch)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.foutBatchfile = QtWidgets.QLineEdit(self.tab_single_batch)
        self.foutBatchfile.setReadOnly(True)
        self.foutBatchfile.setObjectName("foutBatchfile")
        self.horizontalLayout_3.addWidget(self.foutBatchfile)
        self.btnSetFilename = QtWidgets.QPushButton(self.tab_single_batch)
        self.btnSetFilename.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSetFilename.sizePolicy().hasHeightForWidth())
        self.btnSetFilename.setSizePolicy(sizePolicy)
        self.btnSetFilename.setMinimumSize(QtCore.QSize(110, 0))
        self.btnSetFilename.setObjectName("btnSetFilename")
        self.horizontalLayout_3.addWidget(self.btnSetFilename)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.foutWatchdog = QtWidgets.QLineEdit(self.tab_single_batch)
        self.foutWatchdog.setReadOnly(True)
        self.foutWatchdog.setObjectName("foutWatchdog")
        self.horizontalLayout.addWidget(self.foutWatchdog)
        self.btnSetWatchdogDir = QtWidgets.QPushButton(self.tab_single_batch)
        self.btnSetWatchdogDir.setMinimumSize(QtCore.QSize(110, 0))
        self.btnSetWatchdogDir.setObjectName("btnSetWatchdogDir")
        self.horizontalLayout.addWidget(self.btnSetWatchdogDir)
        self.btnWatchdog = QtWidgets.QPushButton(self.tab_single_batch)
        self.btnWatchdog.setCheckable(True)
        self.btnWatchdog.setChecked(False)
        self.btnWatchdog.setDefault(False)
        self.btnWatchdog.setFlat(False)
        self.btnWatchdog.setObjectName("btnWatchdog")
        self.horizontalLayout.addWidget(self.btnWatchdog)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.listFiles = IndexedListWidget(self.tab_single_batch)
        self.listFiles.setMinimumSize(QtCore.QSize(200, 250))
        self.listFiles.setMaximumSize(QtCore.QSize(80000, 50000))
        self.listFiles.setAcceptDrops(True)
        self.listFiles.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listFiles.setObjectName("listFiles")
        self.horizontalLayout_2.addWidget(self.listFiles)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnBrowse = QtWidgets.QPushButton(self.tab_single_batch)
        self.btnBrowse.setEnabled(True)
        self.btnBrowse.setMinimumSize(QtCore.QSize(110, 0))
        self.btnBrowse.setObjectName("btnBrowse")
        self.verticalLayout.addWidget(self.btnBrowse)
        self.btnReset = QtWidgets.QPushButton(self.tab_single_batch)
        self.btnReset.setEnabled(True)
        self.btnReset.setObjectName("btnReset")
        self.BtnFileaction = QtWidgets.QButtonGroup(batch)
        self.BtnFileaction.setObjectName("BtnFileaction")
        self.BtnFileaction.setExclusive(False)
        self.BtnFileaction.addButton(self.btnReset)
        self.verticalLayout.addWidget(self.btnReset)
        spacerItem = QtWidgets.QSpacerItem(20, 255, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.layoutProcess = QtWidgets.QHBoxLayout()
        self.layoutProcess.setObjectName("layoutProcess")
        self.barProgress = QtWidgets.QProgressBar(self.tab_single_batch)
        self.barProgress.setProperty("value", 0)
        self.barProgress.setObjectName("barProgress")
        self.layoutProcess.addWidget(self.barProgress)
        self.radTrace = QtWidgets.QRadioButton(self.tab_single_batch)
        self.radTrace.setChecked(True)
        self.radTrace.setObjectName("radTrace")
        self.RadProcess = QtWidgets.QButtonGroup(batch)
        self.RadProcess.setObjectName("RadProcess")
        self.RadProcess.addButton(self.radTrace)
        self.layoutProcess.addWidget(self.radTrace)
        self.radSpectra = QtWidgets.QRadioButton(self.tab_single_batch)
        self.radSpectra.setEnabled(True)
        self.radSpectra.setObjectName("radSpectra")
        self.RadProcess.addButton(self.radSpectra)
        self.layoutProcess.addWidget(self.radSpectra)
        self.btnAnalyze = QtWidgets.QPushButton(self.tab_single_batch)
        self.btnAnalyze.setObjectName("btnAnalyze")
        self.BtnFileaction.addButton(self.btnAnalyze)
        self.layoutProcess.addWidget(self.btnAnalyze)
        self.btnCancel = QtWidgets.QPushButton(self.tab_single_batch)
        self.btnCancel.setObjectName("btnCancel")
        self.layoutProcess.addWidget(self.btnCancel)
        self.verticalLayout_3.addLayout(self.layoutProcess)
        self.boxTrace = QtWidgets.QGroupBox(self.tab_single_batch)
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
        self.cmbTrace = CharacteristicComboBox(self.boxTrace)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbTrace.sizePolicy().hasHeightForWidth())
        self.cmbTrace.setSizePolicy(sizePolicy)
        self.cmbTrace.setObjectName("cmbTrace")
        self.gridLayout_2.addWidget(self.cmbTrace, 0, 1, 1, 1)
        self.btnImport = QtWidgets.QPushButton(self.boxTrace)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnImport.sizePolicy().hasHeightForWidth())
        self.btnImport.setSizePolicy(sizePolicy)
        self.btnImport.setObjectName("btnImport")
        self.gridLayout_2.addWidget(self.btnImport, 0, 3, 1, 1)
        self.mplTrace = MatplotlibWidget(self.boxTrace)
        self.mplTrace.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplTrace.sizePolicy().hasHeightForWidth())
        self.mplTrace.setSizePolicy(sizePolicy)
        self.mplTrace.setMinimumSize(QtCore.QSize(280, 360))
        self.mplTrace.setMaximumSize(QtCore.QSize(80000, 80000))
        self.mplTrace.setBaseSize(QtCore.QSize(100, 100))
        self.mplTrace.setAutoFillBackground(False)
        self.mplTrace.setObjectName("mplTrace")
        self.gridLayout_2.addWidget(self.mplTrace, 1, 0, 1, 4)
        self.btnRefresh = QtWidgets.QPushButton(self.boxTrace)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRefresh.sizePolicy().hasHeightForWidth())
        self.btnRefresh.setSizePolicy(sizePolicy)
        self.btnRefresh.setObjectName("btnRefresh")
        self.gridLayout_2.addWidget(self.btnRefresh, 0, 2, 1, 1)
        self.verticalLayout_3.addWidget(self.boxTrace)
        self.tabs.addTab(self.tab_single_batch, "")
        self.tab_multi_batch = QtWidgets.QWidget()
        self.tab_multi_batch.setObjectName("tab_multi_batch")
        self.tabs.addTab(self.tab_multi_batch, "")
        self.verticalLayout_2.addWidget(self.tabs)

        self.retranslateUi(batch)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(batch)
        batch.setTabOrder(self.btnBrowse, self.listFiles)
        batch.setTabOrder(self.listFiles, self.btnReset)

    def retranslateUi(self, batch):
        _translate = QtCore.QCoreApplication.translate
        batch.setWindowTitle(_translate("batch", "Batch Analysis"))
        self.btnSetFilename.setText(_translate("batch", "&Set Filename (Export)"))
        self.btnSetWatchdogDir.setText(_translate("batch", "Set Directory (Live)"))
        self.btnWatchdog.setText(_translate("batch", "Activate Live Analysis"))
        self.btnBrowse.setText(_translate("batch", "&Browse Files"))
        self.btnReset.setText(_translate("batch", "Reset"))
        self.radTrace.setText(_translate("batch", "Export + Plot Trace"))
        self.radSpectra.setText(_translate("batch", "Plot Spectra"))
        self.btnAnalyze.setText(_translate("batch", "&Analyze"))
        self.btnCancel.setText(_translate("batch", "Cancel"))
        self.label.setText(_translate("batch", "Select characteristic:"))
        self.btnImport.setText(_translate("batch", "Import Trace"))
        self.btnRefresh.setText(_translate("batch", "Refresh"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_single_batch), _translate("batch", "Single Batch"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_multi_batch), _translate("batch", "Multi Batch"))

from ui.customcombobox import CharacteristicComboBox
from ui.indexedlistwidget import IndexedListWidget
from ui.matplotlibwidget import MatplotlibWidget
