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
        batch.resize(605, 850)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("afm.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        batch.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(batch)
        self.gridLayout.setObjectName("gridLayout")
        self.listFiles = QtWidgets.QListWidget(batch)
        self.listFiles.setObjectName("listFiles")
        self.gridLayout.addWidget(self.listFiles, 1, 0, 3, 1)
        self.btnBrowse = QtWidgets.QPushButton(batch)
        self.btnBrowse.setEnabled(True)
        self.btnBrowse.setObjectName("btnBrowse")
        self.gridLayout.addWidget(self.btnBrowse, 1, 1, 1, 1)
        self.btnClear = QtWidgets.QPushButton(batch)
        self.btnClear.setEnabled(True)
        self.btnClear.setObjectName("btnClear")
        self.BtnFileaction = QtWidgets.QButtonGroup(batch)
        self.BtnFileaction.setObjectName("BtnFileaction")
        self.BtnFileaction.setExclusive(False)
        self.BtnFileaction.addButton(self.btnClear)
        self.gridLayout.addWidget(self.btnClear, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 255, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.boxParameter = QtWidgets.QGroupBox(batch)
        self.boxParameter.setEnabled(True)
        self.boxParameter.setMaximumSize(QtCore.QSize(16777215, 110))
        self.boxParameter.setFlat(False)
        self.boxParameter.setObjectName("boxParameter")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.boxParameter)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.layoutParam1 = QtWidgets.QVBoxLayout()
        self.layoutParam1.setObjectName("layoutParam1")
        self.cbPeakHeight = QtWidgets.QCheckBox(self.boxParameter)
        self.cbPeakHeight.setObjectName("cbPeakHeight")
        self.BtnParameters = QtWidgets.QButtonGroup(batch)
        self.BtnParameters.setObjectName("BtnParameters")
        self.BtnParameters.setExclusive(False)
        self.BtnParameters.addButton(self.cbPeakHeight)
        self.layoutParam1.addWidget(self.cbPeakHeight)
        self.cbPeakArea = QtWidgets.QCheckBox(self.boxParameter)
        self.cbPeakArea.setObjectName("cbPeakArea")
        self.BtnParameters.addButton(self.cbPeakArea)
        self.layoutParam1.addWidget(self.cbPeakArea)
        self.cbBaseline = QtWidgets.QCheckBox(self.boxParameter)
        self.cbBaseline.setObjectName("cbBaseline")
        self.BtnParameters.addButton(self.cbBaseline)
        self.layoutParam1.addWidget(self.cbBaseline)
        self.cbCharacteristicValue = QtWidgets.QCheckBox(self.boxParameter)
        self.cbCharacteristicValue.setObjectName("cbCharacteristicValue")
        self.BtnParameters.addButton(self.cbCharacteristicValue)
        self.layoutParam1.addWidget(self.cbCharacteristicValue)
        self.horizontalLayout.addLayout(self.layoutParam1)
        self.layoutParam2 = QtWidgets.QVBoxLayout()
        self.layoutParam2.setObjectName("layoutParam2")
        self.cbHead = QtWidgets.QCheckBox(self.boxParameter)
        self.cbHead.setObjectName("cbHead")
        self.BtnParameters.addButton(self.cbHead)
        self.layoutParam2.addWidget(self.cbHead)
        self.cbPeakPos = QtWidgets.QCheckBox(self.boxParameter)
        self.cbPeakPos.setObjectName("cbPeakPos")
        self.BtnParameters.addButton(self.cbPeakPos)
        self.layoutParam2.addWidget(self.cbPeakPos)
        self.btnSelectAll = QtWidgets.QPushButton(self.boxParameter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.btnSelectAll.sizePolicy().hasHeightForWidth())
        self.btnSelectAll.setSizePolicy(sizePolicy)
        self.btnSelectAll.setObjectName("btnSelectAll")
        self.layoutParam2.addWidget(self.btnSelectAll)
        self.horizontalLayout.addLayout(self.layoutParam2)
        self.gridLayout.addWidget(self.boxParameter, 4, 0, 1, 2)
        self.layoutProcess = QtWidgets.QHBoxLayout()
        self.layoutProcess.setObjectName("layoutProcess")
        self.barProgress = QtWidgets.QProgressBar(batch)
        self.barProgress.setProperty("value", 0)
        self.barProgress.setObjectName("barProgress")
        self.layoutProcess.addWidget(self.barProgress)
        self.cbUpdatePlots = QtWidgets.QCheckBox(batch)
        self.cbUpdatePlots.setEnabled(True)
        self.cbUpdatePlots.setObjectName("cbUpdatePlots")
        self.layoutProcess.addWidget(self.cbUpdatePlots)
        self.btnCalculate = QtWidgets.QPushButton(batch)
        self.btnCalculate.setEnabled(False)
        self.btnCalculate.setObjectName("btnCalculate")
        self.BtnFileaction.addButton(self.btnCalculate)
        self.layoutProcess.addWidget(self.btnCalculate)
        self.gridLayout.addLayout(self.layoutProcess, 5, 0, 1, 2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.mplConcentration = MatplotlibWidget(batch)
        self.mplConcentration.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplConcentration.sizePolicy().hasHeightForWidth())
        self.mplConcentration.setSizePolicy(sizePolicy)
        self.mplConcentration.setMinimumSize(QtCore.QSize(311, 330))
        self.mplConcentration.setMaximumSize(QtCore.QSize(9999, 9999))
        self.mplConcentration.setObjectName("mplConcentration")
        self.verticalLayout.addWidget(self.mplConcentration)
        self.gridLayout.addLayout(self.verticalLayout, 6, 0, 1, 2)
        self.layoutCSVFile = QtWidgets.QHBoxLayout()
        self.layoutCSVFile.setObjectName("layoutCSVFile")
        self.foutCSV = QtWidgets.QLineEdit(batch)
        self.foutCSV.setReadOnly(True)
        self.foutCSV.setObjectName("foutCSV")
        self.layoutCSVFile.addWidget(self.foutCSV)
        self.btnSetFilename = QtWidgets.QPushButton(batch)
        self.btnSetFilename.setObjectName("btnSetFilename")
        self.layoutCSVFile.addWidget(self.btnSetFilename)
        self.gridLayout.addLayout(self.layoutCSVFile, 0, 0, 1, 2)

        self.retranslateUi(batch)
        QtCore.QMetaObject.connectSlotsByName(batch)
        batch.setTabOrder(self.btnSetFilename, self.btnBrowse)
        batch.setTabOrder(self.btnBrowse, self.cbPeakHeight)
        batch.setTabOrder(self.cbPeakHeight, self.cbBaseline)
        batch.setTabOrder(self.cbBaseline, self.cbHead)
        batch.setTabOrder(self.cbHead, self.foutCSV)
        batch.setTabOrder(self.foutCSV, self.listFiles)
        batch.setTabOrder(self.listFiles, self.btnClear)

    def retranslateUi(self, batch):
        _translate = QtCore.QCoreApplication.translate
        batch.setWindowTitle(_translate("batch", "Batch Analysis"))
        self.btnBrowse.setText(_translate("batch", "&Browse Files"))
        self.btnClear.setText(_translate("batch", "Clear"))
        self.boxParameter.setTitle(_translate("batch", "Parameters"))
        self.cbPeakHeight.setText(_translate("batch", "Peak height"))
        self.cbPeakArea.setText(_translate("batch", "Peak area"))
        self.cbBaseline.setText(_translate("batch", "Baseline"))
        self.cbCharacteristicValue.setText(_translate("batch", "Characteristic Value"))
        self.cbHead.setText(_translate("batch", "Header info"))
        self.cbPeakPos.setText(_translate("batch", "Peak Position"))
        self.btnSelectAll.setText(_translate("batch", "Select All"))
        self.cbUpdatePlots.setText(_translate("batch", "Update Plots"))
        self.btnCalculate.setText(_translate("batch", "&Calculate"))
        self.btnSetFilename.setText(_translate("batch", "&Set Filename"))

from ui.matplotlibwidget import MatplotlibWidget
