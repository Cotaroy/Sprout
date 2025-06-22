from user import User
from saveload import load_user
from pathretriever import R
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import QLabel, QWidget, QScrollArea, QVBoxLayout, QSizePolicy, QFrame, QCheckBox, QHBoxLayout, QPushButton

SCROLL_WIDTH = 250

class MenuScroll(QLabel):
    clicked = QtCore.Signal()

    def __init__(self, x, y, width, height, parent=None):
        super().__init__(parent)

        self.user = load_user('data/test.json')

        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # Optional: hand cursor
        self.open = False

        # center of screen
        self.x = x
        self.y = y
        self.icon_width = width
        self.icon_height = height

        # Scroll area setup (child of the label)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(x, 55, width-35, height*4) #border: none;
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                
            }
            QScrollArea QWidget {
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_size = QRect(x, 55, width-35, height*4)

        # Scroll area content
        self.update_menu()

        self.checkmarked_indices = []

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def toggle_scroll(self):
        if not self.open:
            icon_pixmap = QPixmap(R("assets/scroll_open.png")).scaledToWidth(SCROLL_WIDTH, Qt.SmoothTransformation)
            icon_width = icon_pixmap.width()
            icon_height = icon_pixmap.height()

            self.setGeometry(self.x, 60, icon_width*1.05, icon_height-45)
            self.setPixmap(icon_pixmap)
            self.setScaledContents(True)
            self.scroll_area.show()
            self.open = True
        else:
            icon_pixmap = QPixmap(R("assets/scroll_closed.png")).scaledToWidth(SCROLL_WIDTH, Qt.SmoothTransformation)
            icon_width = icon_pixmap.width()
            icon_height = icon_pixmap.height()

            self.checkmarked_indices.sort(reverse=True)
            print(self.checkmarked_indices)
            for i in self.checkmarked_indices:
                if i < len(self.user.tasks):
                    self.user.complete_task(i)
                    print('task done')
            self.update_menu()

            self.setGeometry(self.x, self.y, icon_width, icon_height)
            self.setPixmap(icon_pixmap)
            self.setScaledContents(True)
            self.scroll_area.hide()
            self.open = False

    def update_menu(self):
        """Update the menu items based on the user's tasks using load_task()."""
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        for i in range(len(self.user.tasks)):
            self.load_task(i, scroll_layout)

        self.create_task_button(scroll_layout)

        self.scroll_area.setWidget(scroll_content)
        self.scroll_area.hide()
#########################################################################
#TODO : Save the user data when the scroll is closed
#########################################################################
    def on_checkbox_toggled(self, index, state):
        print(f"Checkbox for task {index} changed to state {state}")
        if state == 2:
            self.checkmarked_indices.append(index)
        if state == 0:
            if index in self.checkmarked_indices:
                self.checkmarked_indices.remove(index)

    def load_task(self, index: int, target_layout: QVBoxLayout):
        """
        Loads a task from self.user.tasks at the given index into the target layout.

        Assumes each task is a dictionary with 'description' and 'deadline' keys.

        Args:
            self: MainWindow or context that contains self.user.
            index (int): Index of the task to load from self.user.tasks.
            target_layout (QVBoxLayout): The layout to insert the task widgets into.
        """
        if index < 0 or index >= len(self.user.tasks):
            print(f"Invalid task index: {index}")
            return

        task = self.user.tasks[index]
        description = task.description
        deadline = task.deadline.strftime("%Y/%m/%d")

        # Create task UI
        task_widget = QWidget()
        layout = QVBoxLayout(task_widget)
        layout.setGeometry(self.scroll_size)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Horizontal layout with checkbox and label
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        row_layout.setContentsMargins(0, 0, 0, 0)

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(lambda state, idx=index: self.on_checkbox_toggled(idx, state))
        checkbox.setContentsMargins(0, 0, 0, 0)
        checkbox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        checkbox.setStyleSheet("padding: 0px; margin: 0px;")

        label = QLabel(description)
        label.setWordWrap(True)
        label.setMaximumWidth(180)
        label.setContentsMargins(0, 0, 0, 0)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        label.setStyleSheet("padding: 0px; margin: 0px;")

        row_layout.addWidget(checkbox)
        row_layout.addWidget(label)
        row_widget.setMaximumWidth(180)
        layout.addWidget(row_widget)

        deadline_container = QWidget()
        deadline_layout = QVBoxLayout(deadline_container)
        deadline_layout.setContentsMargins(0, 0, 0, 0)
        deadline_layout.setSpacing(0)

        # Create and style deadline label
        deadline_label = QLabel(f"Due: {deadline}")
        deadline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        deadline_label.setStyleSheet("""
            font-size: 12px;
            padding: 0px;
            margin: 0px;
        """)
        deadline_label.setContentsMargins(0, 0, 0, 0)

        # Add label to container layout
        deadline_layout.addWidget(deadline_label)

        # Add container to the main layout
        layout.addWidget(deadline_container)

        target_layout.addWidget(task_widget)

    def create_task_button(self, layout: QVBoxLayout):
        """
        Adds a button to the given layout. When clicked, it hides itself and
        inserts a replacement layout (e.g., with a label).
        """
        # Container widget to hold both button and replacement
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Button
        button = QPushButton("Click me to show more")
        container_layout.addWidget(button)

        # Replacement layout content (hidden initially)
        replacement_widget = QWidget()
        replacement_layout = QVBoxLayout(replacement_widget)
        replacement_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Hello, I replaced the button!")
        replacement_layout.addWidget(label)

        replacement_widget.hide()
        container_layout.addWidget(replacement_widget)

        # Button logic
        def on_button_clicked():
            button.hide()
            replacement_widget.show()

        button.clicked.connect(on_button_clicked)

        # Add container to parent layout
        layout.addWidget(container)