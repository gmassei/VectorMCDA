# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'geoXMCDA.ui'
#
# Created: Sat Sep 27 23:37:42 2014
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(483, 591)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.toolBox = QtGui.QToolBox(Dialog)
        self.toolBox.setStyleSheet(_fromUtf8("\n"
"font: 75 italic 10pt \"MS Shell Dlg 2\";"))
        self.toolBox.setObjectName(_fromUtf8("toolBox"))
        self.CriteriaQTbox = QtGui.QWidget()
        self.CriteriaQTbox.setGeometry(QtCore.QRect(0, 0, 465, 543))
        self.CriteriaQTbox.setObjectName(_fromUtf8("CriteriaQTbox"))
        self.CritListFieldsCBox = QtGui.QComboBox(self.CriteriaQTbox)
        self.CritListFieldsCBox.setGeometry(QtCore.QRect(90, 123, 181, 20))
        self.CritListFieldsCBox.setObjectName(_fromUtf8("CritListFieldsCBox"))
        self.EnvLbl = QtGui.QLabel(self.CriteriaQTbox)
        self.EnvLbl.setGeometry(QtCore.QRect(10, 0, 111, 19))
        self.EnvLbl.setObjectName(_fromUtf8("EnvLbl"))
        self.CritFieldsLbl = QtGui.QLabel(self.CriteriaQTbox)
        self.CritFieldsLbl.setGeometry(QtCore.QRect(2, 122, 81, 23))
        self.CritFieldsLbl.setObjectName(_fromUtf8("CritFieldsLbl"))
        self.CritMapNameLbl = QtGui.QLabel(self.CriteriaQTbox)
        self.CritMapNameLbl.setGeometry(QtCore.QRect(100, 0, 361, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(9)
        self.CritMapNameLbl.setFont(font)
        self.CritMapNameLbl.setTextFormat(QtCore.Qt.AutoText)
        self.CritMapNameLbl.setObjectName(_fromUtf8("CritMapNameLbl"))
        self.CritWeighTableWidget = QtGui.QTableWidget(self.CriteriaQTbox)
        self.CritWeighTableWidget.setGeometry(QtCore.QRect(20, 200, 311, 251))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CritWeighTableWidget.sizePolicy().hasHeightForWidth())
        self.CritWeighTableWidget.setSizePolicy(sizePolicy)
        self.CritWeighTableWidget.setDragEnabled(True)
        self.CritWeighTableWidget.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.CritWeighTableWidget.setAlternatingRowColors(True)
        self.CritWeighTableWidget.setRowCount(0)
        self.CritWeighTableWidget.setObjectName(_fromUtf8("CritWeighTableWidget"))
        self.CritWeighTableWidget.setColumnCount(0)
        self.CritWeighTableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.CritWeighTableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.CritWeighTableWidget.verticalHeader().setHighlightSections(True)
        self.CritRemoveFieldBtn = QtGui.QPushButton(self.CriteriaQTbox)
        self.CritRemoveFieldBtn.setGeometry(QtCore.QRect(380, 120, 75, 24))
        self.CritRemoveFieldBtn.setObjectName(_fromUtf8("CritRemoveFieldBtn"))
        self.CritExtractBtn = QtGui.QPushButton(self.CriteriaQTbox)
        self.CritExtractBtn.setGeometry(QtCore.QRect(350, 200, 101, 251))
        self.CritExtractBtn.setObjectName(_fromUtf8("CritExtractBtn"))
        self.CritHelpBtn = QtGui.QPushButton(self.CriteriaQTbox)
        self.CritHelpBtn.setGeometry(QtCore.QRect(280, 510, 75, 24))
        self.CritHelpBtn.setObjectName(_fromUtf8("CritHelpBtn"))
        self.CritAddFieldBtn = QtGui.QPushButton(self.CriteriaQTbox)
        self.CritAddFieldBtn.setGeometry(QtCore.QRect(290, 120, 75, 24))
        self.CritAddFieldBtn.setObjectName(_fromUtf8("CritAddFieldBtn"))
        self.toXMXCDAButtonBox = QtGui.QDialogButtonBox(self.CriteriaQTbox)
        self.toXMXCDAButtonBox.setGeometry(QtCore.QRect(365, 510, 91, 24))
        self.toXMXCDAButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.toXMXCDAButtonBox.setObjectName(_fromUtf8("toXMXCDAButtonBox"))
        self.groupBox = QtGui.QGroupBox(self.CriteriaQTbox)
        self.groupBox.setGeometry(QtCore.QRect(0, 30, 461, 61))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.btnOutput = QtGui.QToolButton(self.groupBox)
        self.btnOutput.setGeometry(QtCore.QRect(16, 20, 61, 25))
        self.btnOutput.setMinimumSize(QtCore.QSize(0, 25))
        self.btnOutput.setMaximumSize(QtCore.QSize(16777215, 25))
        self.btnOutput.setObjectName(_fromUtf8("btnOutput"))
        self.lineOutput = QtGui.QLineEdit(self.groupBox)
        self.lineOutput.setGeometry(QtCore.QRect(100, 20, 351, 25))
        self.lineOutput.setObjectName(_fromUtf8("lineOutput"))
        self.IDFieldsLbl = QtGui.QLabel(self.CriteriaQTbox)
        self.IDFieldsLbl.setGeometry(QtCore.QRect(12, 460, 81, 23))
        self.IDFieldsLbl.setObjectName(_fromUtf8("IDFieldsLbl"))
        self.IDListFieldsCBox = QtGui.QComboBox(self.CriteriaQTbox)
        self.IDListFieldsCBox.setGeometry(QtCore.QRect(80, 461, 271, 20))
        self.IDListFieldsCBox.setObjectName(_fromUtf8("IDListFieldsCBox"))
        self.toolBox.addItem(self.CriteriaQTbox, _fromUtf8(""))
        self.gridLayout.addWidget(self.toolBox, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.CritListFieldsCBox, self.CritAddFieldBtn)
        Dialog.setTabOrder(self.CritAddFieldBtn, self.CritRemoveFieldBtn)
        Dialog.setTabOrder(self.CritRemoveFieldBtn, self.CritWeighTableWidget)
        Dialog.setTabOrder(self.CritWeighTableWidget, self.CritExtractBtn)
        Dialog.setTabOrder(self.CritExtractBtn, self.CritHelpBtn)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "geoRules", None))
        self.EnvLbl.setText(_translate("Dialog", "Active layer     ", None))
        self.CritFieldsLbl.setText(_translate("Dialog", "Active field", None))
        self.CritRemoveFieldBtn.setText(_translate("Dialog", "Remove", None))
        self.CritExtractBtn.setText(_translate("Dialog", "--> XMCDA file", None))
        self.CritHelpBtn.setText(_translate("Dialog", "Help", None))
        self.CritAddFieldBtn.setText(_translate("Dialog", "Add", None))
        self.groupBox.setTitle(_translate("Dialog", "Output xmcda file", None))
        self.btnOutput.setText(_translate("Dialog", "...", None))
        self.IDFieldsLbl.setText(_translate("Dialog", "ID  field", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.CriteriaQTbox), _translate("Dialog", "Table to XMCDA", None))

