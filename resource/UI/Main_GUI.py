# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Main_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Main_GUI(object):
    def setupUi(self, Main_GUI):
        Main_GUI.setObjectName("Main_GUI")
        Main_GUI.resize(600, 400)
        self.centralwidget = QtWidgets.QWidget(Main_GUI)
        self.centralwidget.setObjectName("centralwidget")
        self.pb_SetAGV = QtWidgets.QPushButton(self.centralwidget)
        self.pb_SetAGV.setGeometry(QtCore.QRect(170, 60, 281, 71))
        self.pb_SetAGV.setObjectName("pb_SetAGV")
        self.pb_AGVGUI = QtWidgets.QPushButton(self.centralwidget)
        self.pb_AGVGUI.setGeometry(QtCore.QRect(170, 200, 281, 71))
        self.pb_AGVGUI.setObjectName("pb_AGVGUI")
        Main_GUI.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Main_GUI)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 23))
        self.menubar.setObjectName("menubar")
        Main_GUI.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Main_GUI)
        self.statusbar.setObjectName("statusbar")
        Main_GUI.setStatusBar(self.statusbar)

        self.retranslateUi(Main_GUI)
        QtCore.QMetaObject.connectSlotsByName(Main_GUI)

    def retranslateUi(self, Main_GUI):
        _translate = QtCore.QCoreApplication.translate
        Main_GUI.setWindowTitle(_translate("Main_GUI", "MainWindow"))
        self.pb_SetAGV.setText(_translate("Main_GUI", "配置机器人"))
        self.pb_AGVGUI.setText(_translate("Main_GUI", "打开机器人"))
