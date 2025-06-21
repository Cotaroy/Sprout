import sys
import autostart
from pathretriever import R
import todolist
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QPixmap, QAction, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QPushButton, QSystemTrayIcon

class MenuScroll(QLabel):
    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # Optional: hand cursor
        self.open = False

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load sprout image
        # Load and resize sprout image
        original_pixmap = QPixmap(R("assets/Base_Bg_Wide.png"))
        scaled_width = 500  # change this as needed
        scaled_pixmap = original_pixmap.scaledToWidth(scaled_width, QtCore.Qt.TransformationMode.SmoothTransformation)

        self.pixmap = scaled_pixmap
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setFixedSize(self.pixmap.size())  # Ensures the full image is visible

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
        self.move_to_bottom_right_above_taskbar()

        # System tray icon
        self.tray_icon = QSystemTrayIcon(QIcon(R("assets/Base_Bg_Wide.png")), self)
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

        self.menu_scroll = MenuScroll(self)
        icon_width = 150
        icon_height = 100

        # Center horizontally, align to bottom (10px above the edge)
        x = (self.pixmap.width() - icon_width) // 2
        y = self.pixmap.height() - icon_height

        self.menu_scroll.setGeometry(x, y, icon_width, icon_height)

        icon_pixmap = QPixmap(R("assets/Base_Bg.png")).scaled(150, 100, QtCore.Qt.KeepAspectRatio,
                                                        QtCore.Qt.SmoothTransformation)

        self.menu_scroll.setPixmap(icon_pixmap)
        self.menu_scroll.setScaledContents(True)

        self.menu_scroll.clicked.connect(self.on_rectangle_clicked)

        # self.text_label = QLabel(self.menu_scroll)
        # self.text_label.setText("")
        # self.text_label.setWordWrap(True)
        # self.text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
        # self.text_label.setGeometry(0, 0, self.menu_scroll.width(), self.menu_scroll.height())
        # self.text_label.setStyleSheet("""
        #     background-color: transparent;
        #     color: white;
        #     padding: 4px 10px;
        #     border-radius: 6px;
        #     font-size: 12px;
        # """)

    def move_to_bottom_right_above_taskbar(self):
        """Move window to bottom-right corner, above taskbar."""
        screen = QApplication.primaryScreen().availableGeometry()
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

    def on_rectangle_clicked(self):
        print("Scroll clicked!")
        change = 80
        if not self.menu_scroll.open:
            self.menu_scroll.move(self.menu_scroll.x(), self.menu_scroll.y() - change)
            self.menu_scroll.open = True
        else:
            self.menu_scroll.move(self.menu_scroll.x(), self.menu_scroll.y() + change)
            self.menu_scroll.open = False



if __name__ == "__main__":
    autostart.add_to_startup()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
