import sys
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QPixmap, QAction, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QSystemTrayIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load image
        pixmap = QPixmap("sprout.png")
        label = QLabel(self)
        label.setPixmap(pixmap)
        self.setCentralWidget(label)

        # Window appearance
        self.setWindowFlags(
            QtCore.Qt.WindowType.Window |
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(pixmap.size())
        self.move_to_bottom_right()

        # System tray setup
        self.tray_icon = QSystemTrayIcon(QIcon("sprout.png"), self)
        tray_menu = QMenu()

        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.showNormal)
        tray_menu.addAction(restore_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("Sprout App")
        self.tray_icon.show()

        self.show()

    def move_to_bottom_right(self):
        screen = QApplication.primaryScreen().geometry()
        window_rect = self.geometry()
        x = screen.width() - window_rect.width()
        y = screen.height() - window_rect.height()
        self.move(x, y)

    def contextMenuEvent(self, event):
        # Right-click on the window
        menu = QMenu(self)
        hide_action = QAction("Hide to Tray", self)
        hide_action.triggered.connect(self.hide)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(hide_action)
        menu.addAction(quit_action)
        menu.exec(event.globalPos())

    def closeEvent(self, event):
        # Intercept close and hide instead
        event.ignore()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray
    window = MainWindow()
    sys.exit(app.exec())
