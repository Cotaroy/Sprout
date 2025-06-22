from saveload import load_user, save_user
from pathretriever import R
from createdateselector import create_date_selector
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import QLabel, QWidget, QScrollArea, QVBoxLayout, QSizePolicy, QFrame, QCheckBox, QHBoxLayout, QPushButton, QLineEdit, QFormLayout, QComboBox, QStackedLayout

from user import Task
from audio_player import AudioPlayer

SCROLL_WIDTH = 250

class MenuScroll(QLabel):
    clicked = QtCore.Signal()

    def __init__(self, user, x, y, width, height, parent=None):
        super().__init__(parent)

        self.user = user
        self.sfx_player = AudioPlayer()

        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # Optional: hand cursor
        self.open = False

        # center of screen
        self.x = x
        self.y = y
        self.icon_width = width
        self.icon_height = height

        self.container = QWidget(self)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Scroll area setup (child of the label)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(x, 55, width-35, height*4)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
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
        self.scroll_area.setMinimumHeight(200)
        self.scroll_area.setMaximumHeight(300)

        # Scroll content
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_size = QRect(x, 55, width-35, height*4)

        self.scroll_area.setWidget(self.scroll_content)
        container_layout.addWidget(self.scroll_area)

        # Load task items into scroll layout
        self.update_menu()

        self.create_history_button(container_layout)

        # Geometry and positioning
        self.container.setGeometry(self.scroll_size)  # same as before

        self.checkmarked_indices = []

    def create_history_button(self, layout: QVBoxLayout):
        """
        Adds a history button that toggles between the main scroll area and a history view.
        """
        print("Creating history button")
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Stacked layout to switch between main view and history
        self.stacked = QStackedLayout()
        container_layout.addLayout(self.stacked)

        # --- Page 0: Scroll Area Container ---
        scroll_page = QWidget()
        scroll_layout = QVBoxLayout(scroll_page)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.addWidget(self.scroll_area)

        history_button = QPushButton("History")
        history_button.setStyleSheet("padding: 4px; margin: 2px;")
        scroll_layout.addWidget(history_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.stacked.addWidget(scroll_page)

        # --- Page 1: History View with Scroll Area ---
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable area for history content
        history_scroll_area = QScrollArea()
        history_scroll_area.setWidgetResizable(True)
        history_scroll_area.setStyleSheet("background-color: transparent;")
        history_scroll_area.setMinimumHeight(200)
        history_scroll_area.setMaximumHeight(300)

        # Content inside the scroll area
        history_scroll_content = QWidget()
        self.history_scroll_layout = QVBoxLayout(history_scroll_content)
        self.history_scroll_layout.setContentsMargins(16, 0, 16, 0)  # Indent left and right

        # Add each finished task as its own widget
        for i in range(len(self.user.finished_tasks)):
            self.load_finished_task(i, self.history_scroll_layout)
            print("index finished task", i)

        self.history_scroll_layout.addStretch()  # Push tasks to the top if few
        history_scroll_area.setWidget(history_scroll_content)
        history_layout.addWidget(history_scroll_area)

        # Back button below the scroll
        back_button = QPushButton("Back")
        back_button.setStyleSheet("padding: 4px; margin: 2px;")
        history_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.stacked.addWidget(history_widget)

        # --- Signal Connections ---
        history_button.clicked.connect(lambda: self.switch_to_history())
        back_button.clicked.connect(lambda: self.switch_to_main())

        layout.addWidget(container)

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
                    self.load_finished_task(len(self.user.finished_tasks) - 1, self.history_scroll_layout)
                    print('task done')
            self.checkmarked_indices = []
            save_user(self.user, 'data/test.json')
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
        scroll_layout.setContentsMargins(16, 0, 16, 0)  # Indent left and right
        for i in range(len(self.user.tasks)):
            self.load_task(i, scroll_layout)
        self.create_task_button(scroll_layout)
        scroll_layout.addStretch()  # Push tasks to the top if few
        self.scroll_area.setWidget(scroll_content)
        self.scroll_area.hide()

    def on_checkbox_toggled(self, index, state):
        print(f"Checkbox for task {index} changed to state {state}")
        if state == 2:
            self.checkmarked_indices.append(index)
            self.sfx_player.play_sfx(R("assets/audio/sfx/Amethyst_step1.ogg"))
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
        deadline = task.deadline.strftime("%Y-%m-%d")

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
            font-size: 14px;
            padding: 0px;
            margin: 0px;
        """)
        deadline_label.setContentsMargins(0, 0, 0, 0)

        # Add label to container layout
        deadline_layout.addWidget(deadline_label)

        # Add container to the main layout
        layout.addWidget(deadline_container)

        target_layout.addWidget(task_widget)

    def load_finished_task(self, index: int, target_layout: QVBoxLayout):
        if index < 0 or index >= len(self.user.finished_tasks):
            print(f"Invalid task index: {index}")
            return

        task = self.user.finished_tasks[index]
        description = task.description
        deadline = task.deadline.strftime("%Y-%m-%d")

        # Task container
        task_widget = QWidget()
        layout = QVBoxLayout(task_widget)
        layout.setSpacing(4)  # Small vertical gap between sections
        layout.setContentsMargins(0, 0, 0, 0)

        # --- Bullet row (like checkbox+label) ---
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)

        bullet = QLabel("•")
        bullet.setStyleSheet("font-size: 16px; color: white;")
        bullet.setFixedWidth(10)

        label = QLabel(description)
        label.setWordWrap(True)
        label.setStyleSheet("padding: 0px; margin: 0px;")
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        row_layout.addWidget(bullet)
        row_layout.addWidget(label)
        layout.addWidget(row_widget)

        # --- Deadline Label ---
        deadline_label = QLabel(f"Completed: {deadline}")
        deadline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        deadline_label.setStyleSheet("""
            font-size: 14px;
            color: white;
            margin: 0px;
        """)
        layout.addWidget(deadline_label)

        # --- Button Row ---
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)

        delete_button = QPushButton("Delete")
        restore_button = QPushButton("Restore")

        button_layout.addStretch()
        button_layout.addWidget(delete_button)
        button_layout.addWidget(restore_button)
        button_layout.addStretch()

        def on_delete_clicked():
            self.user.delete_task(index)
            save_user(self.user, 'data/test.json')

            # --- CLEAR EXISTING TASKS ---
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

            # --- RELOAD ALL TASKS ---
            for i in range(len(self.user.finished_tasks)):
                self.load_finished_task(i, layout)

        def on_restore_clicked():
            self.user.restore_task(index)
            save_user(self.user, 'data/test.json')

            # --- CLEAR EXISTING TASKS ---
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

            # --- RELOAD ALL TASKS ---
            for i in range(len(self.user.finished_tasks)):
                self.load_finished_task(i, layout)

        delete_button.clicked.connect(on_delete_clicked)
        restore_button.clicked.connect(on_restore_clicked)

        layout.addWidget(button_container)

        # --- Add to outer layout ---
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
        button = QPushButton("Add Task")
        button.setStyleSheet("""
            QPushButton {
                background-color: #6b4e3d;  /* fill */
                color: #ffffff;             /* text color */
                border: 1px solid #6b4e3d;  /* border */
                border-radius: 4px;         /* rounded corners */
                padding: 4px 8px;           /* inside spacing */
            }
            QPushButton:hover {
                background-color: #5c4538;  /* hover state */
            }
            QPushButton:pressed {
                background-color: #5c4538;  /* click state */
            }
        """)
        container_layout.addWidget(button)

        # Replacement layout content (hidden initially)
        replacement_widget = QWidget()
        replacement_layout = QVBoxLayout(replacement_widget)
        replacement_layout.setContentsMargins(0, 0, 0, 0)

        task_title = QLineEdit()
        task_title.setPlaceholderText("Enter task description")
        replacement_layout.addWidget(task_title)

        task_deadline = create_date_selector()
        deadline_title = QLabel("Task Deadline")

        font = task_deadline.font()
        font.setPointSize(12)  # Set size in points

        task_deadline.setFont(font)
        deadline_title.setFont(font)
        replacement_layout.addWidget(deadline_title)
        replacement_layout.addWidget(task_deadline)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        cancel_button = QPushButton("Cancel")
        save_button = QPushButton("Save")
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        replacement_layout.addLayout(button_layout)

        replacement_widget.hide()
        container_layout.addWidget(replacement_widget)

        # Button logic
        def on_button_clicked():
            button.hide()
            replacement_widget.show()

        def on_cancel_clicked():
            replacement_widget.hide()
            button.show()

        def on_save_clicked():
            entered_text = task_title.text()
            selected_date = task_deadline.get_selected_date()

            new_task = Task(entered_text, selected_date)
            self.user.tasks.append(new_task)
            save_user(self.user, 'data/test.json')

            # --- CLEAR EXISTING TASKS ---
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

            # --- RELOAD ALL TASKS ---
            for i in range(len(self.user.tasks)):
                self.load_task(i, layout)

            # --- ADD THE TASK CREATION BUTTON BACK AT THE END ---
            self.create_task_button(layout)

        button.clicked.connect(on_button_clicked)
        cancel_button.clicked.connect(on_cancel_clicked)
        save_button.clicked.connect(on_save_clicked)

        # Add container to parent layout
        layout.addWidget(container)

    def switch_to_history(self):
        self.stacked.setCurrentIndex(1)
        self.update_finished_tasks()  # ← reload history scroll layout
        self.update_menu()

    def switch_to_main(self):
        self.update_active_tasks()  # ← rebuild content
        self.stacked.setCurrentIndex(0)

    def update_finished_tasks(self):
        # Clear the layout of finished tasks
        for i in self.checkmarked_indices:
            if i < len(self.user.tasks):
                self.user.complete_task(i)
                self.load_finished_task(len(self.user.finished_tasks) - 1, self.history_scroll_layout)
                print('task done')
        self.checkmarked_indices = []
        while self.history_scroll_layout.count():
            item = self.history_scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        if len(self.user.finished_tasks) == 0:
            empty_label = QLabel("No finished tasks yet! Complete some tasks to see them here.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setWordWrap(True)
            empty_label.setStyleSheet("color: #aaa; font-style: italic; padding: 12px;")
            self.history_scroll_layout.addWidget(empty_label)
        else:
            for i in range(len(self.user.finished_tasks)):
                self.load_finished_task(i, self.history_scroll_layout)

    def update_active_tasks(self):
        # Create new scroll content and layout
        new_scroll_content = QWidget()
        new_scroll_layout = QVBoxLayout(new_scroll_content)
        new_scroll_layout.setContentsMargins(16, 0, 16, 0)  # Indent left and right
        new_scroll_layout.setSpacing(0)

        # Save new references
        self.scroll_content = new_scroll_content
        self.scroll_layout = new_scroll_layout

        # Load tasks
        for i in range(len(self.user.tasks)):
            self.load_task(i, self.scroll_layout)

        # Add creation button
        self.create_task_button(self.scroll_layout)

        # Attach new scroll content
        self.scroll_area.setWidget(self.scroll_content)

        self.scroll_area.show()

