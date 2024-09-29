import os
from PySide6.QtWidgets import (
    QWidget, QGridLayout
)

from src.commands import QCmdGroup
from src.com.abstract import ComProtoBasic


class ExperimentWindow(QWidget):
    CONFIG_DIR = os.path.join(os.getcwd(), "config")
    COMMANDS_CONFIG_FILE = os.path.join(CONFIG_DIR, "commands.json")

    def __init__(self, protocol: ComProtoBasic) -> None:
        """This method initializes the ExperimentWindow class"""
        super().__init__()
        self.setWindowTitle("MACKI - Experiment window")

        self._cmd_group = QCmdGroup.from_JSON(self.COMMANDS_CONFIG_FILE, protocol)

        layout = QGridLayout()
        layout.addWidget(self._cmd_group)

        self.setFixedSize(400, 300)
        self.setLayout(layout)

