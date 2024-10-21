from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from src.utils.numbers import is_number


class ProcedureTable(QTableWidget):
    def __init__(self):
        super().__init__()

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Time [ms]", "Velocity"])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        menu = QMenu()
        remove_action = QAction("Remove row", self)
        remove_action.triggered.connect(self._remove_selected_row)
        add_above_action = QAction("Add row above", self)
        add_above_action.triggered.connect(self._add_row_above)
        add_below_action = QAction("Add row below", self)
        add_below_action.triggered.connect(self._add_row_below)

        menu.addAction(add_above_action)
        menu.addAction(add_below_action)
        menu.addAction(remove_action)
        menu.exec(self.viewport().mapToGlobal(position))

    def _add_row_above(self):
        row_position = self.currentRow()
        self._add_new_row(row_position)

    def _add_row_below(self):
        row_position = self.currentRow()
        self._add_new_row(row_position + 1)

    def _add_new_row(self, row_position):
        self.insertRow(row_position)
        self.setItem(row_position, 0, QTableWidgetItem("0"))
        self.setItem(row_position, 1, QTableWidgetItem("0"))

    def _remove_selected_row(self):
        selected_row = self.currentRow()
        if selected_row >= 0:
            self.removeRow(selected_row)
            self.itemChanged.emit(self.item(selected_row, 0))

    def set_profile(self, profile: list[tuple[int, int]]):
        self.setRowCount(0)
        for time, velocity in profile:
            self._add_new_row(self.rowCount())
            self.item(self.rowCount() - 1, 0).setText(str(time))
            self.item(self.rowCount() - 1, 1).setText(str(velocity))

    def get_velocity_profile(self) -> list[tuple[str, str]] | None:
        velocity_profile = []

        for row in range(self.rowCount()):
            time_item = self.item(row, 0)
            velocity_item = self.item(row, 1)
            if time_item is None or velocity_item is None:
                return None

            time_text = time_item.text()
            velocity_text = velocity_item.text()
            if is_number(time_text) and is_number(velocity_text):
                # table returns value with .0, and cast to int raises exception
                time = int(float(time_text))    # don't even ask XDDDD
                velocity = int(float(velocity_text))
                velocity_profile.append((time, velocity))
            else:
                return None

        return velocity_profile