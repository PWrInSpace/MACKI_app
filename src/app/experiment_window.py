import logging
import random
from typing import Any
from PySide6.QtWidgets import (
    QTabWidget,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QMessageBox
)
from src.app.config import (
    COMMANDS_CONFIG_FILE,
    DATA_PLOT_CONFIG_FILE,
    DATA_TEXT_CONFIG_FILE,
    PARSER_CONFIG_FILE,
    OCTOPUS_EXP_WIN,
    OCTOPUS_CAM_WIN
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from src.commands import QCmdGroup
from src.com.serial import QSerial
# from src.app.cameras_app import QCameraApp
from src.app.commands import ProcedureCommands
from src.data_displays import (
    DataDisplayText, DataDisplayPlot, DataTextBasic
)
from src.data_parser import DataParser

logger = logging.getLogger("experiment_window")


class ExperimentWindow(QTabWidget):
    NACK_COUNTER_LIMIT = 10
    DATA_UPDATE_INTERVAL = 500
    IDX_TAB_EXPERIMENT = 0
    READ_DATA_COMMAND = "data"  # TODO: move the all available commands to a separate file
    SERVICE_DATA_NAME = "Data"
    SERVICE_DATA_COLUMNS = 4

    def __init__(self, protocol: QSerial) -> None:
        """This method initializes the ExperimentWindow class"""
        super().__init__()
        self.setWindowTitle("MACKI - Experiment window")
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMaximizeButtonHint
        )
        self.setWindowIcon(QIcon(OCTOPUS_EXP_WIN))

        self._protocol = protocol

        # Parser
        self._parser = DataParser.from_JSON(PARSER_CONFIG_FILE)
        self._continous_nack_counter = 0

        # Tabs
        experiment_tab = self._experiment_tab()
        service_tab = self._service_widget()

        self.addTab(experiment_tab, "Experiment")
        self.addTab(service_tab, "Service")

        # Data update timer
        self._data_update_timer = QTimer()
        self._data_update_timer.timeout.connect(self._on_update_data_timer)
        # self._data_update_timer.start(self.DATA_UPDATE_INTERVAL)

        for i in range(0, 50):
            self._update_widgets({"time": i, "load_cell": random.randint(0, 10)})

        self._update_widgets(
            {
                "time": 50,
                "load_cell": 3,
                "acceleration": 9.83,
                "pressure tank": 3.5,
                "pressure gripper": 2.5,
                "fill valve": "1",
                "vent valve": "2",
                "motor 1": "2",
                "motor 2": "3"
            }
        )

    def _experiment_tab(self) -> QWidget:
        """  Experiment widget

        Returns:
            QWidget: Experiment widget
        """
        self._cmd_group = ProcedureCommands(self._protocol)
        # self._cameras = QCameraApp(OCTOPUS_CAM_WIN)
        # self._cameras.enable_cameras()

        self._data_plots = DataDisplayPlot.from_JSON(DATA_PLOT_CONFIG_FILE)
        self._data_texts = DataDisplayText.from_JSON(DATA_TEXT_CONFIG_FILE)

        data_layout = QVBoxLayout()
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.addWidget(self._data_plots)
        data_layout.addWidget(self._data_texts)

        data_widget = QWidget()
        data_widget.setContentsMargins(0, 0, 0, 0)
        data_widget.setLayout(data_layout)

        layout = QGridLayout()
        layout.addWidget(self._cmd_group, 0, 0, 1, 1)
        # layout.addWidget(self._cameras, 1, 0, 1, 1)
        layout.addWidget(data_widget, 0, 1, 2, 1)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def _service_widget(self) -> QWidget:
        """Service widget

        Returns:
            QWidget: Service widget
        """
        self._service_cmd = QCmdGroup.from_JSON(COMMANDS_CONFIG_FILE, self._protocol)

        variable_list = self._parser.data_names
        display_cfg = [DataTextBasic(var) for var in variable_list]
        self._service_data = DataDisplayText(
            display_cfg, self.SERVICE_DATA_NAME, self.SERVICE_DATA_COLUMNS
        )

        layout = QGridLayout()
        layout.addWidget(self._service_cmd, 0, 0)
        layout.addWidget(self._service_data, 0, 1)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def _read_data(self) -> str | None:
        """Reads data from the device

        Returns:
            str | None: Data read from the device
        """
        self._protocol.write_command(self.READ_DATA_COMMAND)
        response = self._protocol.read_until_response()

        if response.startswith(self._protocol.ACK):
            return_response = response.replace(self._protocol.ACK, "")
        elif response.startswith(self._protocol.NACK):
            logger.error("Failed to read data - NACK received")
            return_response = None
        elif not response:
            logger.error("Failed to read data - no response")
            return_response = None
        else:
            logger.error(f"Unexpected response: {response}")
            return_response = None

        return return_response

    def _update_widgets(self, data_dict: dict[str, Any]) -> None:
        """Updates the widgets with the data

        Args:
            data_dict (dict[str, Any]): Dictionary with the data keys and values
        """
        if self.currentIndex() == self.IDX_TAB_EXPERIMENT:
            self._data_texts.update_data(data_dict)
            self._data_plots.update_data(data_dict)
        else:
            self._service_data.update_data(data_dict)

    def _check_nack_counter(self) -> None:
        """ Checks the NACK counter and shows a message box if the limit is reached
        """
        if self._continous_nack_counter > self.NACK_COUNTER_LIMIT:
            self._continous_nack_counter = 0
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("Failed to read data - NACK received - check the data_read command!!!")
            msg_box.setWindowTitle("Error")
            msg_box.exec()

    def _on_update_data_timer(self) -> None:
        """Routine to read the data from the device and update the widgets
        """
        if self.isHidden():
            return

        data = self._read_data()
        if data:
            self._continous_nack_counter = 0
            data_dict = self._parser.parse(data)
            self._update_widgets(data_dict)

            logger.info(f"Received data: {data_dict}")
        else:
            self._continous_nack_counter += 1
            self._check_nack_counter()
