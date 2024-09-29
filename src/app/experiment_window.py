import os
from PySide6.QtWidgets import (
    QTabWidget, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import (
    Qt
)
from PySide6.QtGui import QIcon
from src.commands import QCmdGroup
from src.com.abstract import ComProtoBasic
from src.app.cameras_app import QCameraApp
from src.app.commands import ProcedureCommands
from src.data_displays import DataDisplayText, DataDisplayPlot


class ExperimentWindow(QTabWidget):
    CONFIG_DIR = os.path.join(os.getcwd(), "config")
    COMMANDS_CONFIG_FILE = os.path.join(CONFIG_DIR, "service_commands.json")
    DATA_PLOT_CONFIG_FILE = os.path.join(CONFIG_DIR, "experiment_data_plot.json")
    DATA_TEXT_CONFIG_FILE = os.path.join(CONFIG_DIR, "experiment_data_text.json")
    OCTOPUS_LOGO = os.path.join(os.getcwd(), "resources", "octopus.svg")

    def __init__(self, protocol: ComProtoBasic) -> None:
        """This method initializes the ExperimentWindow class"""
        super().__init__()
        self.setWindowTitle("MACKI - Experiment window")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMaximizeButtonHint)
        self.setWindowIcon(QIcon(self.OCTOPUS_LOGO))

        experiment_tab = self._experiment_tab(protocol)
        service_tab = self._service_widget(protocol)

        self.addTab(experiment_tab, "Experiment")
        self.addTab(service_tab, "Service")

    def _experiment_tab(self, protocol: ComProtoBasic) -> QWidget:
        self._cmd_group = ProcedureCommands(protocol)
        self._cameras = QCameraApp()

        self._data_plots = DataDisplayPlot.from_JSON(self.DATA_PLOT_CONFIG_FILE)
        self._data_texts = DataDisplayText.from_JSON(self.DATA_TEXT_CONFIG_FILE)

        data_layout = QVBoxLayout()
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.addWidget(self._data_plots)
        data_layout.addWidget(self._data_texts)

        data_widget = QWidget()
        data_widget.setContentsMargins(0, 0, 0, 0)
        data_widget.setLayout(data_layout)

        layout = QGridLayout()
        layout.addWidget(self._cmd_group, 0, 0, 1, 1)
        layout.addWidget(self._cameras, 1, 0, 1, 1)
        layout.addWidget(data_widget, 0, 1, 2, 1)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def _service_widget(self, protocol: ComProtoBasic) -> QWidget:
        self._service_cmd = QCmdGroup.from_JSON(self.COMMANDS_CONFIG_FILE, protocol)
        # TODO: load variable names from parser, to display all available data
        self._service_data = DataDisplayText.from_JSON(self.DATA_TEXT_CONFIG_FILE)

        layout = QGridLayout()
        layout.addWidget(self._service_cmd, 0, 0)
        layout.addWidget(self._service_data, 0, 1)

        widget = QWidget()
        widget.setLayout(layout)

        return widget
