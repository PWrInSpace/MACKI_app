from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QGroupBox,
    QComboBox,
    QPushButton,
    QGridLayout
)
from PySide6.QtCore import Signal
from src.com.abstract import ComProtoBasic
from src.procedures.procedure_plot import ProcedurePlot
# from src.commands.qt_cmd.q_lock_command import QLockCmd
from src.procedures.procedure_command import ProcedureCmd
from src.procedures.procedure_configurator import ProcedureConfigurator
from src.procedures.procedure_parameters import ProcedureParameters


class ProceduresWidget(QGroupBox):
    BUTTON_TXT_START = "Start"
    BUTTON_TXT_STOP = "Stop"

    def __init__(self, protocol: ComProtoBasic | None = None):
        super().__init__("Procedure control")

        self._configurator = None
        self._current_procedure = ProcedureParameters(
            name="Procedure 1",
            pressurization_time_ms=1000,
            depressurization_time_ms=1500,
            velocity_profile=[(0, 0), (2000, 0), (2000, 2), (3000, 2)],
        )

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        label = QLabel("Procedure name")
        procedure_type = QComboBox()
        procedure_type.addItems(["Procedure 1", "Procedure 2", "Procedure 3"])
        info_button = QPushButton("Procedure values")
        info_button.clicked.connect(self._on_procedure_values_clicked)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(procedure_type, 0, 1)
        layout.addWidget(info_button, 0, 2)
        widget = QWidget()
        widget.setLayout(layout)

        horizontal_bar = QFrame()
        horizontal_bar.setFrameShape(QFrame.HLine)
        horizontal_bar.setFrameShadow(QFrame.Sunken)

        self._procedure_cmd = ProcedureCmd("Procedure", 3)

        # self.setFixedSize(500, 500)
        self._plot = ProcedurePlot()
        self._plot.set_procedure_parameters(self._current_procedure)
        self.layout.addWidget(widget)
        self.layout.addWidget(self._plot)
        self.layout.addWidget(horizontal_bar)
        self.layout.addWidget(self._procedure_cmd)

    def _on_procedure_values_clicked(self):
        self._configurator = ProcedureConfigurator(self._current_procedure)
        self._configurator.show()

    def get_procedure_parameters(self) -> ProcedureParameters:
        return self._current_procedure

    @property
    def start_procedure_clicked(self) -> Signal:
        return self._procedure_cmd.start_clicked

    @property
    def stop_procedure_clicked(self) -> Signal:
        return self._procedure_cmd.stop_clicked
