
import sys
import autostart
from checklist import MenuScroll
from saveload import load_user, save_user
import audio_player

from event import load_event_list
from pathretriever import R
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QFont, QFontDatabase, QPixmap, QAction, QIcon, QMovie
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QPushButton, QSystemTrayIcon, QWidget, QScrollArea, QVBoxLayout, QSizePolicy

from user import run_at_midnight

SCROLL_WIDTH = 250
DEFAULT_DATA_FILE = 'data/default_data.json'
USER_DATA_FILE = 'data/user.json'

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

        self.hidden = False

        self.user = load_user(R(USER_DATA_FILE))
        print(self.user.streaks)

        # AUDIO
        self.sfx_player = audio_player.AudioPlayer()
        self.bgm_player = audio_player.AudioPlayer()

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

        run_at_midnight(self.midnight_update)

        self.menu_scroll.setGeometry(x, y, icon_width, icon_height)

        self.menu_scroll.setPixmap(icon_pixmap)
        self.menu_scroll.setScaledContents(True)



        self.menu_scroll.clicked.connect(self.change_background_on_toggle)

        # Play GIF animation on top of main window at startup, matching background size and position
        gif_x = self.image_label.x()
        gif_y = self.image_label.y()
        gif_width = self.image_label.width()
        gif_height = self.image_label.height()

        Event = load_event_list()

        if self.user.event_index < len(Event):
            self.begin_event(gif_x, gif_y, gif_width, gif_height, Event[self.user.event_index])

    def left_arrow_key_pressed_event(self, event):
        boundaries = [2, 4, 7, 14, 20]
        for i in range(len(boundaries)):
            if self.user.streaks <= boundaries[i]:
                self.user.streaks = boundaries[(i - 1) % len(boundaries)]
                self.set_background()
                print(f"Streaks updated to: {self.user.streaks}")
                self.menu_scroll.update_subtitle()
                return

        self.user.streaks = 14
        self.set_background()
        print(f"Streaks updated to: {self.user.streaks}")
        self.menu_scroll.update_subtitle()

    def right_arrow_key_pressed_event(self, event):
        boundaries = [2, 4, 7, 14, 20]
        for i in range(len(boundaries)):
            if self.user.streaks <= boundaries[i]:
                self.user.streaks = boundaries[(i + 1) % len(boundaries)]
                self.set_background()
                print(f"Streaks updated to: {self.user.streaks}")
                self.menu_scroll.update_subtitle()
                return
        self.user.streaks = 2
        self.set_background()
        print(f"Streaks updated to: {self.user.streaks}")
        self.menu_scroll.update_subtitle()

    def midnight_update(self):
        self.menu_scroll.update_subtitle()
        self.user.check_streak()

    def change_background_on_toggle(self):
        self.set_background()
        self.menu_scroll.toggle_scroll()
        self.sfx_player.play_sfx(R("assets/audio/sfx/scroll.mp3"))

    def choose_background(self):
        if self.user.streaks >= 20:
            return 'Base_Bg5.png'
        elif self.user.streaks >= 14:
            return 'Base_Bg4.png'
        elif self.user.streaks >= 7:
            return 'Base_Bg3.png'
        elif self.user.streaks >= 4:
            return 'Base_Bg2.png'
        elif self.user.streaks >= 2:
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
        self.hidden = True

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)

        reset_action = QAction("Reset Data", self)
        reset_action.triggered.connect(self.reset_data)

        menu.addAction(hide_action)
        menu.addAction(quit_action)
        menu.addAction(reset_action)
        menu.exec(event.globalPos())

    def reset_data(self):
        """Reset user data to default."""
        self.user = load_user(DEFAULT_DATA_FILE)
        save_user(self.user, R(USER_DATA_FILE))
        self.menu_scroll.update_subtitle()
        self.menu_scroll.update_menu()
        self.set_background()
        print("Data reset to default.")

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

    def on_speech_bubble_clicked(self, event):
        if self.speech_bubble.curr_index < len(self.speech_bubble.script) - 1:
            self.speech_bubble.curr_index += 1
            self.speech_text.setText(self.speech_bubble.script[self.speech_bubble.curr_index])
        else:
            self.speech_bubble.hide()

    def begin_event(self, x, y, width, height, messages):
        self.user.event_index += 1

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
                self.text_bubble_text.setText("")
                self._start_typewriter_animation(text)
            else:
                # Fallback: recreate text label if missing
                bubble_width = self.text_bubble_label.width()
                bubble_height = self.text_bubble_label.height()
                margin_x = int(bubble_width * 0.18)
                margin_y = 20
                self.text_bubble_text = QLabel(self.text_bubble_label)
                self.text_bubble_text.setText("")
                self.text_bubble_text.setWordWrap(True)
                self.text_bubble_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.text_bubble_text.setGeometry(margin_x, margin_y, bubble_width - 2 * margin_x, bubble_height - 2 * margin_y)
                self.text_bubble_text.setStyleSheet("background: transparent; color: black; font-size: 16px; padding: 4px;")
                self.text_bubble_text.show()
                self._start_typewriter_animation(text)
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
        self.text_bubble_text.setText("")
        self.text_bubble_text.setWordWrap(True)
        self.text_bubble_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        margin_x = int(bubble_width * 0.18)
        margin_y = 20
        self.text_bubble_text.setGeometry(margin_x, margin_y, bubble_width - 2 * margin_x, bubble_height - 2 * margin_y)
        self.text_bubble_text.setStyleSheet("background: transparent; color: black; font-size: 16px; padding: 4px;")
        self.text_bubble_text.show()
        # Make bubble clickable for next message
        self.text_bubble_label.mousePressEvent = self._on_text_bubble_clicked
        self._start_typewriter_animation(text)

    def _on_text_bubble_clicked(self, event):
        # If animation is running, finish instantly
        if hasattr(self, '_typewriter_timer') and self._typewriter_timer.isActive() and self._typewriter_index <= len(self._typewriter_text):
            self._typewriter_timer.stop()
            self.sfx_player.stop()
            self.text_bubble_text.setText(self._typewriter_text)
        else:
            # Advance to next message or hide if at the end
            if self.speech_bubble.curr_index < len(self.speech_bubble.script) - 1:
                self.speech_bubble.curr_index += 1
                next_text = self.speech_bubble.script[self.speech_bubble.curr_index]
                self.text_bubble_text.setText("")
                self._start_typewriter_animation(next_text)
            else:
                self.speech_bubble.hide()
                self.text_bubble_label.hide()
                # After bubble is done, wait 0.3s then play walking_out.gif
                QtCore.QTimer.singleShot(300, self.play_walking_out_gif)

    def _start_typewriter_animation(self, full_text):
        # Cancel any previous animation
        if hasattr(self, '_typewriter_timer') and self._typewriter_timer is not None:
            self._typewriter_timer.stop()
            self._typewriter_timer.deleteLater()
        self._typewriter_index = 0
        self._typewriter_text = full_text
        self._typewriter_timer = QtCore.QTimer(self)
        self._typewriter_timer.timeout.connect(self._update_typewriter_text)
        self._typewriter_timer.start(25)  # Adjust speed here (ms per character)
        self.sfx_player.play_sfx(R("assets/audio/sfx/irene.mp3"))  # Play sound effect for 2 seconds

    def _update_typewriter_text(self):
        if self._typewriter_index <= len(self._typewriter_text):
            self.text_bubble_text.setText(self._typewriter_text[:self._typewriter_index])
            self._typewriter_index += 1
        else:
            self.sfx_player.stop()
            self._typewriter_timer.stop()

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
            save_user(self.user, R(USER_DATA_FILE))
            self.movie.stop()
            self.gif_label.deleteLater()
        # App resumes normal operation (no further action needed)


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Z:
            self.left_arrow_key_pressed_event(event)
            print("z pressed")
        elif event.key() == QtCore.Qt.Key_X:
            self.right_arrow_key_pressed_event(event)
            print("x pressed")
        else:
            super().keyPressEvent(event)

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

    bgm_player = audio_player.AudioPlayer()
    if window.user.streaks >= 22:
            bgm_player.play_bg_track(R("assets/audio/bgm/bigbig_tree_track.mp3"))
    elif window.user.streaks >= 15:
        bgm_player.play_bg_track(R("assets/audio/bgm/big_tree.mp3"))
    elif window.user.streaks >= 9:
        bgm_player.play_bg_track(R("assets/audio/bgm/mid_tree.mp3"))
    elif window.user.streaks >= 5:
        bgm_player.play_bg_track(R("assets/audio/bgm/tree_teen.mp3"))
    elif window.user.streaks >= 3:
        bgm_player.play_bg_track(R("assets/audio/bgm/sprout.mp3"))
    else:
        bgm_player.play_bg_track(R("assets/audio/bgm/brown_noise.mp3"))

    window.show()
    sys.exit(app.exec())
