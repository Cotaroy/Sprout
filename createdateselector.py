from PySide6.QtWidgets import QWidget, QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtCore import QDate, Qt
import datetime


class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        if self.view().isVisible():  # Only allow scrolling when dropdown is open
            super().wheelEvent(event)
        else:
            event.ignore()  # Prevent accidental scrolling

def create_date_selector():
        """Returns a QWidget containing a year|month|day dropdown selector with a date accessor."""
        class DateSelectorWidget(QWidget):
            def __init__(self):
                super().__init__()

                # Components
                self.year_combo = NoScrollComboBox()
                self.month_combo = NoScrollComboBox()
                self.day_combo = NoScrollComboBox()
                self.date_label = QLabel()

                # Populate years
                for year in range(2024, 2051):
                    self.year_combo.addItem(str(year))

                # Populate months
                for month in range(1, 13):
                    self.month_combo.addItem(str(month))

                # Set properties
                self.year_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self.month_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self.day_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                # ensure they never shrink below text width
                self.year_combo.setMinimumContentsLength(4)    # “2025”
                self.month_combo.setMinimumContentsLength(2)   # “12”
                self.day_combo.setMinimumContentsLength(2)     # “31”
                for combo in (self.year_combo, self.month_combo, self.day_combo):
                    combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)

                self.year_combo.setStyleSheet("font-size:14px;")
                self.month_combo.setStyleSheet("font-size:14px;")
                self.day_combo.setStyleSheet("font-size:14px;")
                
                # Layouts
                hbox = QHBoxLayout()
                hbox.addWidget(self.year_combo, 2)
                hbox.addWidget(self.month_combo, 1)
                hbox.addWidget(self.day_combo, 1)
                hbox.setSpacing(4)

                vbox = QVBoxLayout(self)
                vbox.addLayout(hbox)
                vbox.addWidget(self.date_label)

                # Signals
                self.year_combo.currentIndexChanged.connect(self.update_days)
                self.month_combo.currentIndexChanged.connect(self.update_days)
                self.day_combo.currentIndexChanged.connect(self.update_label)

                # Initialize current date
                today = QDate.currentDate()
                self.year_combo.setCurrentText(str(today.year()))
                self.month_combo.setCurrentText(str(today.month()))
                self.update_days()

            def update_days(self):
                year = int(self.year_combo.currentText())
                month = int(self.month_combo.currentText())
                days_in_month = QDate(year, month, 1).daysInMonth()

                current_day = self.day_combo.currentText()
                self.day_combo.clear()
                for day in range(1, days_in_month + 1):
                    self.day_combo.addItem(str(day))

                if current_day.isdigit() and int(current_day) <= days_in_month:
                    self.day_combo.setCurrentText(current_day)

                self.update_label()

            def update_label(self):
                y = self.year_combo.currentText()
                m = self.month_combo.currentText()
                d = self.day_combo.currentText()
                self.date_label.setText(f"Selected date: {y}-{m.zfill(2)}-{d.zfill(2)}")
                self.date_label.setStyleSheet("font-size: 14px;")

            def get_selected_date(self):
                """Returns the selected date as a QDate object."""
                y = int(self.year_combo.currentText())
                m = int(self.month_combo.currentText())
                d = int(self.day_combo.currentText())
                return datetime.date(y, m, d)

        return DateSelectorWidget()
