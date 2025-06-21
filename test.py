from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor
import sys

class CornerPond(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(200, 100)  # Size of the window

        self._old_pos = None

        # Sample content
        layout = QVBoxLayout()
        label = QLabel("Cornerpond\n(mini app)")
        label.setStyleSheet("color: white; font-size: 14px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._old_pos is not None:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.pos() + delta)
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._old_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(30, 30, 30, 180))  # Semi-transparent background
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def move_to_bottom_right(self):
        screen = QGuiApplication.primaryScreen()
        geometry = screen.availableGeometry()
        x = geometry.right() - self.width() - 10  # 10px margin from edge
        y = geometry.bottom() - self.height() - 10
        self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CornerPond()
    window.show()
    sys.exit(app.exec())
