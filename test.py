import sys

from PySide6 import QtGui
from PySide6.QtGui import QPixmap, QAction
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QMenu


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        pixmap = QtGui.QPixmap("sprout.png")
        print(pixmap)
        label = QLabel(self)
        label.setPixmap(pixmap)
        self.setCentralWidget(label)

        self.setWindowFlags(
            QtCore.Qt.WindowType.Window |
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool
        )

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # Resize window to image size
        self.resize(pixmap.size())

        self.move_to_bottom_right()

        self.show()

    def move_to_bottom_right(self):
        screen = QApplication.primaryScreen().geometry()
        window_rect = self.geometry()

        x = screen.width() - window_rect.width()
        y = screen.height() - window_rect.height()

        self.move(x, y)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        menu.exec(event.globalPos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()
