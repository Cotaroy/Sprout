import sys
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QPixmap, QAction, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QSystemTrayIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load sprout image
        self.pixmap = QPixmap("sprout.png")
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.pixmap)
        self.setCentralWidget(self.image_label)

        self.text_label = QLabel(self)
        self.text_label.setText("This is a long message that should wrap into multiple lines properly.")
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.text_label.setFixedWidth(self.pixmap.width())
        self.text_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
        """)

        # Window appearance
        self.setWindowFlags(
            QtCore.Qt.WindowType.Window |
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # Resize and position
        self.resize(self.pixmap.size())
        self.position_text_label()
        self.move_to_bottom_right_above_taskbar()

        # System tray icon
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

    def position_text_label(self):
        """Place text box at the bottom of the image, adjusting height dynamically."""
        self.text_label.adjustSize()
        label_height = self.text_label.height()
        self.text_label.setGeometry(0, self.pixmap.height() - label_height, self.pixmap.width(), label_height)

    def move_to_bottom_right_above_taskbar(self):
        """Move window to bottom-right corner, above taskbar."""
        screen = QApplication.primaryScreen().availableGeometry()  # Use availableGeometry instead of geometry
        window_rect = self.geometry()

        x = screen.x() + screen.width() - window_rect.width()
        y = screen.y() + screen.height() - window_rect.height()

        self.move(x, y)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        hide_action = QAction("Hide to Tray", self)
        hide_action.triggered.connect(self.hide)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(hide_action)
        menu.addAction(quit_action)
        menu.exec(event.globalPos())

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_text_label()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    sys.exit(app.exec())
