# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui',
# licensing of 'gui.ui' applies.
#
# Created: Sat Aug 24 16:03:52 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_GisWindow(object):
    def setupUi(self, GisWindow):
        GisWindow.setObjectName("GisWindow")
        GisWindow.resize(938, 577)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/map.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        GisWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(GisWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        GisWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(GisWindow)
        self.statusbar.setObjectName("statusbar")
        GisWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(GisWindow)
        self.toolBar.setObjectName("toolBar")
        GisWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionZoom_in = QtWidgets.QAction(GisWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/zoom_in.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoom_in.setIcon(icon1)
        self.actionZoom_in.setObjectName("actionZoom_in")
        self.actionZoom_out = QtWidgets.QAction(GisWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/zoom_out.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoom_out.setIcon(icon2)
        self.actionZoom_out.setObjectName("actionZoom_out")
        self.actionZoom_default = QtWidgets.QAction(GisWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/icons/zoom_default.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoom_default.setIcon(icon3)
        self.actionZoom_default.setObjectName("actionZoom_default")
        self.actionNight_mode = QtWidgets.QAction(GisWindow)
        self.actionNight_mode.setCheckable(True)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/icons/map (night).svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNight_mode.setIcon(icon4)
        self.actionNight_mode.setObjectName("actionNight_mode")
        self.toolBar.addAction(self.actionZoom_in)
        self.toolBar.addAction(self.actionZoom_out)
        self.toolBar.addAction(self.actionZoom_default)
        self.toolBar.addAction(self.actionNight_mode)

        self.retranslateUi(GisWindow)
        QtCore.QMetaObject.connectSlotsByName(GisWindow)

    def retranslateUi(self, GisWindow):
        GisWindow.setWindowTitle(QtWidgets.QApplication.translate("GisWindow", "GridCal - GIS", None, -1))
        self.toolBar.setWindowTitle(QtWidgets.QApplication.translate("GisWindow", "toolBar", None, -1))
        self.actionZoom_in.setText(QtWidgets.QApplication.translate("GisWindow", "Zoom in", None, -1))
        self.actionZoom_out.setText(QtWidgets.QApplication.translate("GisWindow", "Zoom out", None, -1))
        self.actionZoom_default.setText(QtWidgets.QApplication.translate("GisWindow", "Zoom default", None, -1))
        self.actionNight_mode.setText(QtWidgets.QApplication.translate("GisWindow", "Night mode", None, -1))

from icons_rc import *

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    GisWindow = QtWidgets.QMainWindow()
    ui = Ui_GisWindow()
    ui.setupUi(GisWindow)
    GisWindow.show()
    sys.exit(app.exec_())

