# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_main(object):
    def setupUi(self, main):
        main.setObjectName("main")
        main.setWindowModality(QtCore.Qt.NonModal)
        main.resize(1200, 1000)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(main.sizePolicy().hasHeightForWidth())
        main.setSizePolicy(sizePolicy)
        main.setMinimumSize(QtCore.QSize(540, 830))
        main.setMaximumSize(QtCore.QSize(16777215, 16777215))
        main.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        main.setAcceptDrops(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../gfx/dispersion.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        main.setWindowIcon(icon)
        main.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.centralwidget = QtWidgets.QWidget(main)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.layoutInformation = QtWidgets.QVBoxLayout()
        self.layoutInformation.setSpacing(3)
        self.layoutInformation.setObjectName("layoutInformation")
        self.boxBasic = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boxBasic.sizePolicy().hasHeightForWidth())
        self.boxBasic.setSizePolicy(sizePolicy)
        self.boxBasic.setMinimumSize(QtCore.QSize(250, 0))
        self.boxBasic.setObjectName("boxBasic")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.boxBasic)
        self.verticalLayout.setContentsMargins(9, 9, -1, -1)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblCentralWavelength = QtWidgets.QLabel(self.boxBasic)
        self.lblCentralWavelength.setObjectName("lblCentralWavelength")
        self.verticalLayout.addWidget(self.lblCentralWavelength)
        self.tinCentralWavelength = QtWidgets.QLineEdit(self.boxBasic)
        self.tinCentralWavelength.setObjectName("tinCentralWavelength")
        self.verticalLayout.addWidget(self.tinCentralWavelength)
        self.lblDispersion = QtWidgets.QLabel(self.boxBasic)
        self.lblDispersion.setObjectName("lblDispersion")
        self.verticalLayout.addWidget(self.lblDispersion)
        self.tinDispersion = QtWidgets.QLineEdit(self.boxBasic)
        self.tinDispersion.setObjectName("tinDispersion")
        self.verticalLayout.addWidget(self.tinDispersion)
        self.cbInvertSpectrum = QtWidgets.QCheckBox(self.boxBasic)
        self.cbInvertSpectrum.setEnabled(True)
        self.cbInvertSpectrum.setObjectName("cbInvertSpectrum")
        self.verticalLayout.addWidget(self.cbInvertSpectrum)
        self.lblFitting = QtWidgets.QLabel(self.boxBasic)
        self.lblFitting.setObjectName("lblFitting")
        self.verticalLayout.addWidget(self.lblFitting)
        self.clistFitting = CheckableListWidget(self.boxBasic)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clistFitting.sizePolicy().hasHeightForWidth())
        self.clistFitting.setSizePolicy(sizePolicy)
        self.clistFitting.setMinimumSize(QtCore.QSize(0, 100))
        self.clistFitting.setMaximumSize(QtCore.QSize(16777215, 140))
        self.clistFitting.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.clistFitting.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
        self.clistFitting.setObjectName("clistFitting")
        self.verticalLayout.addWidget(self.clistFitting)
        self.cbBaselineCorrection = QtWidgets.QCheckBox(self.boxBasic)
        self.cbBaselineCorrection.setChecked(True)
        self.cbBaselineCorrection.setObjectName("cbBaselineCorrection")
        self.verticalLayout.addWidget(self.cbBaselineCorrection)
        self.cbNormalizeData = QtWidgets.QCheckBox(self.boxBasic)
        self.cbNormalizeData.setChecked(False)
        self.cbNormalizeData.setObjectName("cbNormalizeData")
        self.verticalLayout.addWidget(self.cbNormalizeData)
        self.rcbCalibration = RichCheckbox(self.boxBasic)
        self.rcbCalibration.setObjectName("rcbCalibration")
        self.verticalLayout.addWidget(self.rcbCalibration)
        self.layoutInformation.addWidget(self.boxBasic)
        self.boxResults = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boxResults.sizePolicy().hasHeightForWidth())
        self.boxResults.setSizePolicy(sizePolicy)
        self.boxResults.setMinimumSize(QtCore.QSize(250, 0))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.boxResults.setFont(font)
        self.boxResults.setObjectName("boxResults")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.boxResults)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lblCharacteristicValue = QtWidgets.QLabel(self.boxResults)
        self.lblCharacteristicValue.setEnabled(True)
        self.lblCharacteristicValue.setObjectName("lblCharacteristicValue")
        self.verticalLayout_2.addWidget(self.lblCharacteristicValue)
        self.toutCharacteristicValue = QtWidgets.QLineEdit(self.boxResults)
        self.toutCharacteristicValue.setReadOnly(True)
        self.toutCharacteristicValue.setObjectName("toutCharacteristicValue")
        self.verticalLayout_2.addWidget(self.toutCharacteristicValue)
        self.lblPeakHeight = QtWidgets.QLabel(self.boxResults)
        self.lblPeakHeight.setObjectName("lblPeakHeight")
        self.verticalLayout_2.addWidget(self.lblPeakHeight)
        self.toutPeakHeight = QtWidgets.QLineEdit(self.boxResults)
        self.toutPeakHeight.setReadOnly(True)
        self.toutPeakHeight.setObjectName("toutPeakHeight")
        self.verticalLayout_2.addWidget(self.toutPeakHeight)
        self.lblPeakArea = QtWidgets.QLabel(self.boxResults)
        self.lblPeakArea.setObjectName("lblPeakArea")
        self.verticalLayout_2.addWidget(self.lblPeakArea)
        self.toutPeakArea = QtWidgets.QLineEdit(self.boxResults)
        self.toutPeakArea.setReadOnly(True)
        self.toutPeakArea.setObjectName("toutPeakArea")
        self.verticalLayout_2.addWidget(self.toutPeakArea)
        self.lblBaseline = QtWidgets.QLabel(self.boxResults)
        self.lblBaseline.setObjectName("lblBaseline")
        self.verticalLayout_2.addWidget(self.lblBaseline)
        self.toutBaseline = QtWidgets.QLineEdit(self.boxResults)
        self.toutBaseline.setReadOnly(True)
        self.toutBaseline.setObjectName("toutBaseline")
        self.verticalLayout_2.addWidget(self.toutBaseline)
        self.layoutInformation.addWidget(self.boxResults)
        self.boxAddInformation = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boxAddInformation.sizePolicy().hasHeightForWidth())
        self.boxAddInformation.setSizePolicy(sizePolicy)
        self.boxAddInformation.setMinimumSize(QtCore.QSize(250, 0))
        self.boxAddInformation.setMaximumSize(QtCore.QSize(183, 16777215))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.boxAddInformation.setFont(font)
        self.boxAddInformation.setObjectName("boxAddInformation")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.boxAddInformation)
        self.verticalLayout_4.setContentsMargins(-1, -1, -1, 9)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.lblTimeInfo = QtWidgets.QLabel(self.boxAddInformation)
        self.lblTimeInfo.setObjectName("lblTimeInfo")
        self.verticalLayout_4.addWidget(self.lblTimeInfo)
        self.toutTimeInfo = QtWidgets.QLineEdit(self.boxAddInformation)
        self.toutTimeInfo.setReadOnly(True)
        self.toutTimeInfo.setObjectName("toutTimeInfo")
        self.verticalLayout_4.addWidget(self.toutTimeInfo)
        self.lblDiffWavelength = QtWidgets.QLabel(self.boxAddInformation)
        self.lblDiffWavelength.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDiffWavelength.sizePolicy().hasHeightForWidth())
        self.lblDiffWavelength.setSizePolicy(sizePolicy)
        self.lblDiffWavelength.setMinimumSize(QtCore.QSize(0, 43))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 63, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 63, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 63, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        self.lblDiffWavelength.setPalette(palette)
        self.lblDiffWavelength.setObjectName("lblDiffWavelength")
        self.verticalLayout_4.addWidget(self.lblDiffWavelength)
        self.listInformation = QtWidgets.QListWidget(self.boxAddInformation)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listInformation.sizePolicy().hasHeightForWidth())
        self.listInformation.setSizePolicy(sizePolicy)
        self.listInformation.setMaximumSize(QtCore.QSize(1000, 1000))
        self.listInformation.setObjectName("listInformation")
        self.verticalLayout_4.addWidget(self.listInformation)
        self.layoutInformation.addWidget(self.boxAddInformation)
        self.gridLayout.addLayout(self.layoutInformation, 0, 1, 4, 1)
        self.layoutFile = QtWidgets.QHBoxLayout()
        self.layoutFile.setObjectName("layoutFile")
        self.lblFilename = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFilename.sizePolicy().hasHeightForWidth())
        self.lblFilename.setSizePolicy(sizePolicy)
        self.lblFilename.setMaximumSize(QtCore.QSize(40, 30))
        self.lblFilename.setObjectName("lblFilename")
        self.layoutFile.addWidget(self.lblFilename)
        self.toutFilename = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toutFilename.sizePolicy().hasHeightForWidth())
        self.toutFilename.setSizePolicy(sizePolicy)
        self.toutFilename.setMaximumSize(QtCore.QSize(800, 30))
        self.toutFilename.setReadOnly(True)
        self.toutFilename.setObjectName("toutFilename")
        self.layoutFile.addWidget(self.toutFilename)
        self.btnFileOpen = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnFileOpen.sizePolicy().hasHeightForWidth())
        self.btnFileOpen.setSizePolicy(sizePolicy)
        self.btnFileOpen.setMaximumSize(QtCore.QSize(70, 30))
        self.btnFileOpen.setObjectName("btnFileOpen")
        self.layoutFile.addWidget(self.btnFileOpen)
        self.gridLayout.addLayout(self.layoutFile, 0, 0, 1, 1)
        self.boxRaw = QtWidgets.QGroupBox(self.centralwidget)
        self.boxRaw.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boxRaw.sizePolicy().hasHeightForWidth())
        self.boxRaw.setSizePolicy(sizePolicy)
        self.boxRaw.setMinimumSize(QtCore.QSize(450, 350))
        self.boxRaw.setMaximumSize(QtCore.QSize(1000, 1670))
        self.boxRaw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.boxRaw.setObjectName("boxRaw")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.boxRaw)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.mplRaw = MatplotlibWidget(self.boxRaw)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplRaw.sizePolicy().hasHeightForWidth())
        self.mplRaw.setSizePolicy(sizePolicy)
        self.mplRaw.setMinimumSize(QtCore.QSize(400, 200))
        self.mplRaw.setMaximumSize(QtCore.QSize(900, 600))
        self.mplRaw.setObjectName("mplRaw")
        self.verticalLayout_3.addWidget(self.mplRaw)
        self.gridLayout.addWidget(self.boxRaw, 1, 0, 1, 1)
        self.boxProcessed = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boxProcessed.sizePolicy().hasHeightForWidth())
        self.boxProcessed.setSizePolicy(sizePolicy)
        self.boxProcessed.setMinimumSize(QtCore.QSize(450, 350))
        self.boxProcessed.setMaximumSize(QtCore.QSize(1000, 1670))
        self.boxProcessed.setObjectName("boxProcessed")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.boxProcessed)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.mplProcessed = MatplotlibWidget(self.boxProcessed)
        self.mplProcessed.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplProcessed.sizePolicy().hasHeightForWidth())
        self.mplProcessed.setSizePolicy(sizePolicy)
        self.mplProcessed.setMinimumSize(QtCore.QSize(400, 200))
        self.mplProcessed.setMaximumSize(QtCore.QSize(900, 500))
        self.mplProcessed.setObjectName("mplProcessed")
        self.verticalLayout_5.addWidget(self.mplProcessed)
        self.gridLayout.addWidget(self.boxProcessed, 2, 0, 1, 1)
        main.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 20))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSave = QtWidgets.QMenu(self.menuFile)
        self.menuSave.setEnabled(True)
        self.menuSave.setObjectName("menuSave")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        main.setMenuBar(self.menubar)
        self.actOpen = QtWidgets.QAction(main)
        self.actOpen.setObjectName("actOpen")
        self.actOpenBatch = QtWidgets.QAction(main)
        self.actOpenBatch.setObjectName("actOpenBatch")
        self.actSaveRaw = QtWidgets.QAction(main)
        self.actSaveRaw.setEnabled(False)
        self.actSaveRaw.setObjectName("actSaveRaw")
        self.actSaveProcessed = QtWidgets.QAction(main)
        self.actSaveProcessed.setEnabled(False)
        self.actSaveProcessed.setObjectName("actSaveProcessed")
        self.menuSave.addAction(self.actSaveRaw)
        self.menuSave.addAction(self.actSaveProcessed)
        self.menuFile.addAction(self.actOpen)
        self.menuFile.addAction(self.menuSave.menuAction())
        self.menuFile.addSeparator()
        self.menuTools.addAction(self.actOpenBatch)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())

        self.retranslateUi(main)
        QtCore.QMetaObject.connectSlotsByName(main)
        main.setTabOrder(self.btnFileOpen, self.tinCentralWavelength)
        main.setTabOrder(self.tinCentralWavelength, self.toutPeakHeight)
        main.setTabOrder(self.toutPeakHeight, self.toutPeakArea)

    def retranslateUi(self, main):
        _translate = QtCore.QCoreApplication.translate
        main.setWindowTitle(_translate("main", "OES-Spectra-Analysis"))
        self.boxBasic.setTitle(_translate("main", "Basic Information"))
        self.lblCentralWavelength.setText(_translate("main", "Central Wavelength (nm):"))
        self.tinCentralWavelength.setInputMask(_translate("main", "000.0000"))
        self.lblDispersion.setText(_translate("main", "Dispersion (nm/px):"))
        self.tinDispersion.setInputMask(_translate("main", "0.00000000"))
        self.cbInvertSpectrum.setText(_translate("main", "Invert Spectrum"))
        self.lblFitting.setText(_translate("main", "Fitting:"))
        self.cbBaselineCorrection.setText(_translate("main", "Baseline correction"))
        self.cbNormalizeData.setText(_translate("main", "Normalize data"))
        self.rcbCalibration.setText(_translate("main", "Calibration"))
        self.boxResults.setTitle(_translate("main", "Results"))
        self.lblCharacteristicValue.setText(_translate("main", "Characteristic Value:"))
        self.lblPeakHeight.setText(_translate("main", "Peak Height:"))
        self.lblPeakArea.setText(_translate("main", "Peak Area:"))
        self.lblBaseline.setText(_translate("main", "Baseline:"))
        self.boxAddInformation.setTitle(_translate("main", "Additional Information"))
        self.lblTimeInfo.setText(_translate("main", "Time information of file:"))
        self.lblDiffWavelength.setText(_translate("main", "Difference in readout \n"
"wavelength and entered \n"
"wavelength!"))
        self.lblFilename.setText(_translate("main", "File:"))
        self.btnFileOpen.setText(_translate("main", "Browse"))
        self.boxRaw.setTitle(_translate("main", "Raw Spectrum"))
        self.boxProcessed.setTitle(_translate("main", "Processed Spectrum"))
        self.menuFile.setTitle(_translate("main", "&Spectrum"))
        self.menuSave.setTitle(_translate("main", "Export..."))
        self.menuTools.setTitle(_translate("main", "&Analysis"))
        self.actOpen.setText(_translate("main", "&Open"))
        self.actOpenBatch.setText(_translate("main", "Analyze &Multiple Files"))
        self.actSaveRaw.setText(_translate("main", "Raw Data"))
        self.actSaveProcessed.setText(_translate("main", "Fitted result"))

from ui.checkablelistwidget import CheckableListWidget
from ui.matplotlibwidget import MatplotlibWidget
from ui.richcheckbox import RichCheckbox
