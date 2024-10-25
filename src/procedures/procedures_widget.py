import json
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

    def __init__(self, procedure_config_file: str, protocol: ComProtoBasic | None = None) -> None:
        super().__init__("Procedure control")

        self._configurator = None
        self._current_procedure = None
        self._procedures = {}
        self._procedure_config_file = procedure_config_file

        self._load_procedures()
        self._init_ui()
        self._set_current_procedure()

    def _load_procedures(self):
        with open(self._procedure_config_file, "r") as file:
            json_dict = json.load(file)

        if len(json_dict) == 0:
            raise ValueError("No procedures loaded")

        for procedure_dict in json_dict:
            procedure = ProcedureParameters.from_dict(procedure_dict)
            self._procedures[procedure.name] = procedure

    def _save_procedures(self):
        with open(self._procedure_config_file, "w") as file:
            json_dict = [procedure.to_dict() for procedure in self._procedures.values()]
            json.dump(json_dict, file, indent=2)

    def _init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        label = QLabel("Procedure name")
        self._procedure_type = QComboBox()
        self._procedure_type.addItems(list(self._procedures.keys()))
        self._procedure_type.currentIndexChanged.connect(self._set_current_procedure)

        info_button = QPushButton("Procedure values")
        info_button.clicked.connect(self._on_procedure_values_clicked)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(self._procedure_type, 0, 1)
        layout.addWidget(info_button, 0, 2)
        widget = QWidget()
        widget.setLayout(layout)

        horizontal_bar = QFrame()
        horizontal_bar.setFrameShape(QFrame.HLine)
        horizontal_bar.setFrameShadow(QFrame.Sunken)

        self._procedure_cmd = ProcedureCmd("Procedure", 3)

        # self.setFixedSize(500, 500)
        self._plot = ProcedurePlot()
        self.layout.addWidget(widget)
        self.layout.addWidget(self._plot)
        self.layout.addWidget(horizontal_bar)
        self.layout.addWidget(self._procedure_cmd)

    def _on_procedure_values_clicked(self):
        self._configurator = ProcedureConfigurator(self._current_procedure)
        self._configurator.show()
        self._configurator.closed.connect(self._on_configurator_closed)
        self._configurator.updated.connect(self._on_procedure_updated)

        self._procedure_type.setEnabled(False)

    def _set_current_procedure(self) -> None:
        procedure_name = self._procedure_type.currentText()
        self._current_procedure = self._procedures[procedure_name]
        self._plot.set_procedure_parameters(self._current_procedure)

    def _on_procedure_updated(self, procedure: ProcedureParameters):
        self._current_procedure = procedure
        self._procedures[procedure.name] = procedure
        self._plot.set_procedure_parameters(self._current_procedure)
        self._save_procedures()

    def _on_configurator_closed(self):
        self._procedure_type.setEnabled(True)

    def get_procedure_parameters(self) -> ProcedureParameters:
        return self._current_procedure

    def append_live_data(self, velocity: float, time: dict) -> None:
        self._plot.append_live_velocity(velocity, time)

    def is_procedure_running(self) -> bool:
        return self._procedure_cmd.is_running()

    @property
    def start_procedure_clicked(self) -> Signal:
        return self._procedure_cmd.start_clicked

    @property
    def stop_procedure_clicked(self) -> Signal:
        return self._procedure_cmd.stop_clicked
