import sys
import autostart
import checklist
from saveload import load_user

from event import Event
from pathretriever import R
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QPixmap, QAction, QIcon, QFontDatabase, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QPushButton, QSystemTrayIcon, QWidget, QScrollArea, QVBoxLayout, QSizePolicy

SCROLL_WIDTH = 250

class EventSpeechBubble(QLabel):
    clicked = QtCore.Signal()

    def __init__(self, script, parent=None):
        super().__init__(parent)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # Optional: hand cursor
        self.script = script
        self.curr_index = 0


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load sprout image
        # Load and resize sprout image
        original_pixmap = QPixmap(R("assets/Base_Bg.png"))
        scaled_width = 300  # change this as needed
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

        icon_pixmap = QPixmap(R("assets/scroll_closed.png")).scaledToWidth(SCROLL_WIDTH,
                                                                        QtCore.Qt.SmoothTransformation)

        icon_width = icon_pixmap.width()
        icon_height = icon_pixmap.height()

        # Center horizontally, align to bottom (10px above the edge)
        x = (self.pixmap.width() - icon_width) // 2
        y = self.pixmap.height() - icon_height

        self.menu_scroll = checklist.MenuScroll(x, y, icon_width, icon_height, self)

        self.menu_scroll.setGeometry(x, y, icon_width, icon_height)

        self.menu_scroll.setPixmap(icon_pixmap)
        self.menu_scroll.setScaledContents(True)

        self.setup_speech_bubble()
        self.speech_bubble.hide()

        self.menu_scroll.clicked.connect(self.menu_scroll.toggle_scroll)


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

    def on_button_click(self, index):
        print(f"Button {index + 1} clicked!")

    def setup_speech_bubble(self):
        bubble_pixmap = QPixmap(R("assets/speech_bubble.png")).scaledToWidth(SCROLL_WIDTH,
                                                                          QtCore.Qt.SmoothTransformation)

        self.speech_bubble = EventSpeechBubble(['Hello', 'there', 'i', 'am', 'bob'], self)
        bubble_width = bubble_pixmap.width()
        bubble_height = bubble_pixmap.height()

        # Center horizontally, align to bottom (10px above the edge)
        x = (self.pixmap.width() - bubble_width) // 2
        y = self.pixmap.height() - bubble_height
        self.speech_bubble.setGeometry(x, y, bubble_width, bubble_height)

        self.speech_bubble.setPixmap(bubble_pixmap)
        self.speech_bubble.setScaledContents(True)

        self.speech_text = QLabel(self.speech_bubble)
        self.speech_text.setText(self.speech_bubble.script[0])
        self.speech_text.setWordWrap(True)
        self.speech_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.speech_text.setGeometry(bubble_width // 2, bubble_height // 2, self.menu_scroll.width(), self.menu_scroll.height())
        self.speech_text.setStyleSheet("""
                                                background-color: transparent;
                                                color: white;
                                                padding: 4px 10px;
                                                border-radius: 6px;
                                                font-size: 12px;
                                            """)
        self.speech_bubble.clicked.connect(self.on_speech_bubble_clicked)

    def on_speech_bubble_clicked(self):
        if self.speech_bubble.curr_index < len(self.speech_bubble.script) - 1:
            self.speech_bubble.curr_index += 1
            self.speech_text.setText(self.speech_bubble.script[self.speech_bubble.curr_index])
        else:
            self.speech_bubble.hide()


if __name__ == "__main__":
    autostart.add_to_startup()
    app = QApplication(sys.argv)
    
    font_id = QFontDatabase.addApplicationFont(R("assets/font/Atlantistextregular-qZv0.ttf"))
    if font_id == -1:
        print("Failed to load font")
    else:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 14))  # Set globally
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
