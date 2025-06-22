import sys
import autostart
from checklist import MenuScroll
from saveload import load_user


from event import Event
from pathretriever import R
from PySide6 import QtWidgets, QtCore, QtGui,  QMovie
from PySide6.QtGui import QPixmap, QAction, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QPushButton, QSystemTrayIcon, QWidget, QScrollArea, QVBoxLayout, QSizePolicy

from user import run_at_midnight

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

        self.user = load_user('data/test.json')
        print(self.user.streaks)

        # Load sprout image
        # Load and resize sprout image
        original_pixmap = QPixmap(R("assets/Base_Bg.png"))
        scaled_width = 300  # change this as needed
        scaled_pixmap = original_pixmap.scaledToWidth(scaled_width, QtCore.Qt.TransformationMode.SmoothTransformation)

        self.pixmap = scaled_pixmap
        self.image_label = QLabel(self)
        self.set_background()

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

        self.menu_scroll = MenuScroll(self.user, x, y, icon_width, icon_height, self)

        run_at_midnight(self.user.check_streak)

        self.menu_scroll.setGeometry(x, y, icon_width, icon_height)

        self.menu_scroll.setPixmap(icon_pixmap)
        self.menu_scroll.setScaledContents(True)



        self.menu_scroll.clicked.connect(self.change_background_on_toggle)

        # Play GIF animation on top of main window at startup, matching background size and position
        gif_x = self.image_label.x()
        gif_y = self.image_label.y()
        gif_width = self.image_label.width()
        gif_height = self.image_label.height()

        Event = [['Hello', 'there', 'i', 'am', 'bob']]
        self.begin_event(gif_x, gif_y, gif_width, gif_height, Event[0])

    def change_background_on_toggle(self):
        self.set_background()
        self.menu_scroll.toggle_scroll()
        self.user.streaks += 2

    def choose_background(self):
        if self.user.streaks >= 22:
            return 'Base_Bg5.png'
        elif self.user.streaks >= 15:
            return 'Base_Bg4.png'
        elif self.user.streaks >= 9:
            return 'Base_Bg3.png'
        elif self.user.streaks >= 5:
            return 'Base_Bg2.png'
        elif self.user.streaks >= 3:
            return 'Base_Bg1.png'
        else:
            return 'Base_Bg.png'

    def set_background(self):
        original_pixmap = QPixmap(R(f"assets/{self.choose_background()}"))
        scaled_width = 300
        scaled_pixmap = original_pixmap.scaledToWidth(scaled_width,
                                                      QtCore.Qt.TransformationMode.SmoothTransformation)
        self.pixmap = scaled_pixmap
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setFixedSize(self.pixmap.size())
        self.image_label.lower()

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

    def setup_speech_bubble(self, messages):
        bubble_pixmap = QPixmap(R("assets/speech_bubble.png")).scaledToWidth(SCROLL_WIDTH,
                                                                          QtCore.Qt.SmoothTransformation)

        self.speech_bubble = EventSpeechBubble(messages, self)
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

    def begin_event(self, x, y, width, height, messages):

        self.setup_speech_bubble(messages)
        self.speech_bubble.hide()
        # Overlay the GIF label on top of the main window, matching background
        if hasattr(self, 'gif_label'):
            self.gif_label.deleteLater()
        self.gif_label = QLabel(self)
        self.gif_label.setGeometry(x, y, width, height)
        self.gif_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.gif_label.setStyleSheet('background: transparent;')
        self.movie = QMovie(R(f"assets/walk_in.gif"))
        if not self.movie.isValid():
            print(f"GIF not found or invalid: assets/walk_in.gif")
        self.gif_label.setMovie(self.movie)
        self.gif_label.setScaledContents(True)
        self.gif_label.show()
        self.gif_label.raise_()  # Ensure it's on top
        self._gif_target_frame = 2  # 0-based index, so frame 3 is index 2
        self.movie.frameChanged.connect(self._on_gif_frame_changed)
        self.movie.start()

    def set_stand_still_png(self):
        if hasattr(self, 'gif_label'):
            self.gif_label.setMovie(None)
            standstill_movie = QMovie(R("assets/stand_still.gif"))
            if not standstill_movie.isValid():
                print("stand_still.gif not found or invalid!")
                return
            self.gif_label.setMovie(standstill_movie)
            self.gif_label.setScaledContents(True)
            standstill_movie.start()
        # Show text bubble after stationary gif begins playing
        # wait 0.15 seconds before showing text bubble
        QtCore.QTimer.singleShot(200, lambda: self.show_text_bubble())

    def _on_gif_frame_changed(self, frame_number):
        if hasattr(self, '_gif_target_frame') and hasattr(self, 'movie') and frame_number == self._gif_target_frame:
            self.movie.stop()
            self.set_stand_still_png()

    def show_text_bubble(self):
        # Always show the first message in the sequence
        if hasattr(self, 'speech_bubble'):
            self.speech_bubble.curr_index = 0
            text = self.speech_bubble.script[0]
        else:
            text = ""
        # If a text bubble already exists, just update the text
        if hasattr(self, 'text_bubble_label') and self.text_bubble_label.isVisible():
            if hasattr(self, 'text_bubble_text'):
                self.text_bubble_text.setText(text)
            else:
                # Fallback: recreate text label if missing
                bubble_width = self.text_bubble_label.width()
                bubble_height = self.text_bubble_label.height()
                margin_x = int(bubble_width * 0.18)
                margin_y = 20
                self.text_bubble_text = QLabel(self.text_bubble_label)
                self.text_bubble_text.setText(text)
                self.text_bubble_text.setWordWrap(True)
                self.text_bubble_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.text_bubble_text.setGeometry(margin_x, margin_y, bubble_width - 2 * margin_x, bubble_height - 2 * margin_y)
                self.text_bubble_text.setStyleSheet("background: transparent; color: black; font-size: 16px; padding: 4px;")
                self.text_bubble_text.show()
            return
        # Otherwise, create a new text bubble
        if hasattr(self, 'text_bubble_label'):
            self.text_bubble_label.deleteLater()
        bubble_pixmap = QPixmap(R("assets/text_bubble.png"))
        bubble_width = int(self.width() // 1.7)
        bubble_height = int(self.height() // 1.7)
        bubble_x = 0
        bubble_y = 80
        self.text_bubble_label = QLabel(self)
        self.text_bubble_label.setPixmap(bubble_pixmap.scaled(bubble_width, bubble_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.text_bubble_label.setGeometry(bubble_x, bubble_y, bubble_width, bubble_height)
        self.text_bubble_label.setScaledContents(True)
        self.text_bubble_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.text_bubble_label.setStyleSheet('background: transparent;')
        self.text_bubble_label.show()
        # Add a text label on top of the bubble
        if hasattr(self, 'text_bubble_text'):
            self.text_bubble_text.deleteLater()
        self.text_bubble_text = QLabel(self.text_bubble_label)
        self.text_bubble_text.setText(text)
        self.text_bubble_text.setWordWrap(True)
        self.text_bubble_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        margin_x = int(bubble_width * 0.18)
        margin_y = 20
        self.text_bubble_text.setGeometry(margin_x, margin_y, bubble_width - 2 * margin_x, bubble_height - 2 * margin_y)
        self.text_bubble_text.setStyleSheet("background: transparent; color: black; font-size: 16px; padding: 4px;")
        self.text_bubble_text.show()
        # Make bubble clickable for next message
        self.text_bubble_label.mousePressEvent = self._on_text_bubble_clicked

    def _on_text_bubble_clicked(self, event):
        # Advance to the next message or hide if at the end
        if self.speech_bubble.curr_index < len(self.speech_bubble.script) - 1:
            self.speech_bubble.curr_index += 1
            self.text_bubble_text.setText(self.speech_bubble.script[self.speech_bubble.curr_index])
        else:
            self.speech_bubble.hide()
            self.text_bubble_label.hide()
            # After bubble is done, wait 0.3s then play walking_out.gif
            QtCore.QTimer.singleShot(300, self.play_walking_out_gif)

    def play_walking_out_gif(self):
        # Play walking_out.gif at the same position as the sprout
        gif_x = self.image_label.x()
        gif_y = self.image_label.y()
        gif_width = self.image_label.width()
        gif_height = self.image_label.height()
        if hasattr(self, 'gif_label'):
            self.gif_label.deleteLater()
        self.gif_label = QLabel(self)
        self.gif_label.setGeometry(gif_x, gif_y, gif_width, gif_height)
        self.gif_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.gif_label.setStyleSheet('background: transparent;')
        self.movie = QMovie(R("assets/walking_out.gif"))
        if not self.movie.isValid():
            print("GIF not found or invalid: assets/walking_out.gif")
        self.gif_label.setMovie(self.movie)
        self.gif_label.setScaledContents(True)
        self.gif_label.show()
        self.gif_label.raise_()
        self.movie.frameChanged.connect(self.walking_out_frame_changed)
        self.movie.start()
        self._gif_target_frame = 2  # 0-based index, so frame 3 is index 2

    def walking_out_frame_changed(self, frame_number):
        if hasattr(self, 'movie') and frame_number == self._gif_target_frame:
            # wait 0.3 seconds
            QtCore.QTimer.singleShot(300, self._on_walking_out_finished)


    def _on_walking_out_finished(self):
        if hasattr(self, 'gif_label'):
            self.movie.stop()
            self.gif_label.deleteLater()
        # App resumes normal operation (no further action needed)


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
