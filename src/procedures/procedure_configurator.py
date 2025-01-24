from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QGridLayout,
    QMessageBox,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
from src.procedures.procedure_parameters import ProcedureParameters
from src.procedures.procedure_plot import ProcedurePlot
from src.procedures.procedure_table import ProcedureTable
from src.utils.numbers import is_number

from src.app.config import OCTOPUS_PROC_CONFIG_WIN  # FIXME: should not be included here


class ProcedureConfigurator(QWidget):
    closed = Signal()
    updated = Signal(ProcedureParameters)

    def __init__(self, params: ProcedureParameters):
        super().__init__()

        # FIXME: implement better solution for the icon path
        self.setWindowIcon(QIcon(OCTOPUS_PROC_CONFIG_WIN))

        self._value_changed = False
        self._init_ui(params)

        self._press_input.textChanged.connect(self._on_procedure_param_changed)
        self._depr_input.textChanged.connect(self._on_procedure_param_changed)
        self._table.itemChanged.connect(self._on_procedure_param_changed)

    def _init_ui(self, params: ProcedureParameters):
        """Initialize the UI

        Args:
            params (ProcedureParameters): The procedure parameters to initialize the UI with
        """
        self.setWindowTitle(params.name)

        press_label = QLabel("Pressurization Time [ms]")
        self._press_input = QLineEdit()
        self._press_input.setText(str(params.press_time_ms))

        depr_label = QLabel("Depressurization Time [ms]")
        self._depr_input = QLineEdit()
        self._depr_input.setText(str(params.depr_time_ms))

        self._table = ProcedureTable()
        self._table.set_profile(params.velocity_profile)

        self.plot = ProcedurePlot()
        self.plot.set_procedure_parameters(params)

        layout = QGridLayout()
        layout.addWidget(press_label, 0, 0)
        layout.addWidget(self._press_input, 0, 1)
        layout.addWidget(depr_label, 1, 0)
        layout.addWidget(self._depr_input, 1, 1)
        layout.addWidget(self._table, 2, 0, 1, 2)
        layout.addWidget(self.plot, 0, 2, 3, 1)
        self.setLayout(layout)

    def _on_procedure_param_changed(self):
        """Callback for the procedure parameters change"""
        self._value_changed = True
        params = self.generate_procedure_params()
        if params:
            self.plot.set_procedure_parameters(params)

    def generate_procedure_params(self, skip_check: bool = True) -> ProcedureParameters:
        """Generate the procedure parameters from the input fields

        Args:
            skip_check (bool, optional): Skip the check for the parameters. Defaults to True.

        Returns:
            ProcedureParameters: The procedure parameters object or None if the input is invalid
        """
        press_time_text = self._press_input.text()
        depr_time_text = self._depr_input.text()

        press_time_ms = float(press_time_text) if is_number(press_time_text) else None
        depr_time_ms = float(depr_time_text) if is_number(depr_time_text) else None

        velocity_profile = self._table.get_velocity_profile()
        if velocity_profile is None:
            return None

        return ProcedureParameters(
            name=self.windowTitle(),
            press_time_ms=press_time_ms,
            depr_time_ms=depr_time_ms,
            velocity_profile=velocity_profile,
            skip_check=skip_check,
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
            "Save Changes",
            "You have changed the parameters. Do you want to save them?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        return reply == QMessageBox.Yes

    def closeEvent(self, event):
        """Close the window and emit the updated signal if the user wants to save the changes

        Args:
            event (_type_): The close event
        """
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
