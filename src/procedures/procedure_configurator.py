from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QGridLayout,
    QTableWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import Signal
from src.procedures.procedure_parameters import ProcedureParameters
from src.procedures.procedure_plot import ProcedurePlot
from src.procedures.procedure_table import ProcedureTable
from src.utils.numbers import is_number


class ProcedureConfigurator(QWidget):
    closed = Signal()
    updated = Signal(ProcedureParameters)

    def __init__(self, params: ProcedureParameters):
        super().__init__()

        self._value_changed = False

        # Create layout
        layout = QGridLayout()
        self.setWindowTitle(params.name)

        # Create and add pressurization time label and text box in grid layout
        press_label = QLabel("Pressurization Time [ms]")
        self.press_input = QLineEdit()
        layout.addWidget(press_label, 0, 0)
        layout.addWidget(self.press_input, 0, 1)

        # Create and add depressurization time label and text box in grid layout
        depr_label = QLabel("Depressurization Time [ms]")
        self.depr_input = QLineEdit()
        layout.addWidget(depr_label, 1, 0)
        layout.addWidget(self.depr_input, 1, 1)

        # Create and add table
        self.table = ProcedureTable()
        layout.addWidget(self.table, 2, 0, 1, 2)

        self.plot = ProcedurePlot()
        layout.addWidget(self.plot, 0, 2, 3, 1)
        self.plot.set_procedure_parameters(params)

        # Set layout
        self.press_input.setText(str(params.pressurization_time_ms))
        self.depr_input.setText(str(params.depressurization_time_ms))
        self.add_items_to_table(params.velocity_profile)

        self.press_input.textChanged.connect(self.on_item_changed)
        self.depr_input.textChanged.connect(self.on_item_changed)
        self.table.itemChanged.connect(self.on_item_changed)

        self.setLayout(layout)

    def add_items_to_table(self, items):
        for time, velocity in items:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(time)))
            self.table.setItem(row_position, 1, QTableWidgetItem(str(velocity)))

    def on_item_changed(self):
        self._value_changed = True
        params = self.generate_procedure_params()
        if params:
            self.plot.set_procedure_parameters(params)

    def generate_procedure_params(self, skip_check: bool = True) -> ProcedureParameters:
        press_time_text = self.press_input.text()
        depr_time_text = self.depr_input.text()

        press_time_ms = float(press_time_text) if is_number(press_time_text) else None
        depr_time_ms = float(depr_time_text) if is_number(depr_time_text) else None

        velocity_profile = self.table.get_velocity_profile()
        if velocity_profile is None:
            return None

        return ProcedureParameters(
            name=self.windowTitle(),
            pressurization_time_ms=press_time_ms,
            depressurization_time_ms=depr_time_ms,
            velocity_profile=velocity_profile,
            skip_check=skip_check
        )

    def _save_changes_window(self) -> bool:
        """Show a message box to save the changes

        Returns:
            bool: True if the user wants to save the changes, False otherwise
        """
        if self._value_changed is False:
            return False

        reply = QMessageBox.question(
            self,
            'Save Changes',
            'You have changed the parameters. Do you want to save them?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        return reply == QMessageBox.Yes

    def closeEvent(self, event):
        if self._save_changes_window():
            try:
                params = self.generate_procedure_params(skip_check=False)
                self.updated.emit(params)
                self.closed.emit()
            except ValueError as e:
                event.ignore()
                QMessageBox.critical(self, "Error", str(e))
        else:
            event.accept()
            self.closed.emit()
