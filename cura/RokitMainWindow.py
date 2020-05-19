
from PyQt5.QtCore import Qt, QCoreApplication, QTimer, QRectF
from PyQt5.QtGui import QPixmap, QPainter

from UM.Qt.Bindings.MainWindow import MainWindow
from UM.Application import Application

class RokitMainWindow(MainWindow):
    """MainWindow subclass that provides the main window."""

    def __init__(self, parent = None):
        super(RokitMainWindow, self).__init__(parent)
        
        Application.getInstance().setMainWindow(self)

        target = QRectF(10.0, 20.0, 80.0, 60.0)
        source = QRectF(0.0, 0.0, 70.0, 40.0)
        self._pixmap = QPixmap(Resources.getPath(Resources.Images, "rokit-splash.png"))
        self._painter = QPainter(this)
        self._painter.drawPixmap(target, pixmap, source)
