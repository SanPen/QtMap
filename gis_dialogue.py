import sys
# from PySide2.QtCore import *
# from PySide2.QtGui import *
from PySide2.QtWidgets import *

from gui import *
from lightmap import *


class GISWindow(QMainWindow):

    def __init__(self, parent=None):
        """

        :param parent:
        """
        QMainWindow.__init__(self)
        self.ui = Ui_GisWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('GridCal - GIS')

        # scroll area
        self.map_ = LightMaps(self)
        self.setCentralWidget(self.map_)

        # action linking
        self.ui.actionNight_mode.triggered.connect(self.map_.toggle_night_mode)
        self.ui.actionZoom_in.triggered.connect(self.map_.zoom_increase)
        self.ui.actionZoom_out.triggered.connect(self.map_.zoom_decrease)

    def msg(self, text, title="Warning"):
        """
        Message box
        :param text: Text to display
        :param title: Name of the window
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        # msg.setInformativeText("This is additional information")
        msg.setWindowTitle(title)
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = GISWindow()
    window.resize(1.61 * 700.0, 600.0)  # golden ratio
    window.show()
    sys.exit(app.exec_())

