import os
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout
)
from PySide6.QtCore import (
    Qt
)
from PySide6.QtGui import QIcon
from src.commands import QCmdGroup
from src.com.abstract import ComProtoBasic
from src.app.cameras_app import QCameraApp
from src.data_displays import DataDisplayText, DataDisplayPlot


class ExperimentWindow(QWidget):
    CONFIG_DIR = os.path.join(os.getcwd(), "config")
    COMMANDS_CONFIG_FILE = os.path.join(CONFIG_DIR, "commands.json")
    DATA_PLOT_CONFIG_FILE = os.path.join(CONFIG_DIR, "data_plot.json")
    DATA_TEXT_CONFIG_FILE = os.path.join(CONFIG_DIR, "data_text.json")
    OCTOPUS_LOGO = os.path.join(os.getcwd(), "resources", "octopus.svg")

    def __init__(self, protocol: ComProtoBasic) -> None:
        """This method initializes the ExperimentWindow class"""
        super().__init__()
        self.setWindowTitle("MACKI - Experiment window")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMaximizeButtonHint)
        self.setWindowIcon(QIcon(self.OCTOPUS_LOGO))

        self._cmd_group = QCmdGroup.from_JSON(self.COMMANDS_CONFIG_FILE, protocol)
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

        # self.setFixedSize(600, 300)
        self.setLayout(layout)
