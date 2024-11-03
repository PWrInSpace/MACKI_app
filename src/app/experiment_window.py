import logging
from typing import Any
from PySide6.QtWidgets import QTabWidget, QWidget, QGridLayout, QVBoxLayout, QMessageBox
from PySide6.QtCore import QThread
from src.app.config import (
    COMMANDS_CONFIG_FILE,
    DATA_PLOT_CONFIG_FILE,
    DATA_TEXT_CONFIG_FILE,
    PARSER_CONFIG_FILE,
    PROCEDURES_CONFIG_FILE,
    OCTOPUS_EXP_WIN,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from src.commands import QCmdGroup
from src.com.serial import QSerial

from app.cameras_app import QCameraApp
from src.procedures.procedures_widget import ProceduresWidget
from src.procedures.procedure_parameters import ProcedureParameters
from src.data_displays import DataDisplayText, DataDisplayPlot, DataTextBasic

# from src.data_parser import DataParser
from src.data_logger import DataLogger
from src.data_parser.data_parser_string import DataParserString

logger = logging.getLogger("experiment_window")


class ExperimentWindow(QTabWidget):
    NACK_COUNTER_LIMIT = 3
    DATA_UPDATE_INTERVAL = 150
    IDX_TAB_EXPERIMENT = 0
    # TODO: move the all available commands to a separate file
    READ_DATA_COMMAND = "data"
    PROCEDURE_START_COMMAND = "procedure"
    PROCEDURE_STOP_COMMAND = "procedure_stop"
    SERVICE_DATA_NAME = "Data"
    PROCEDURE_PLOT_TIME = "procedure_time"
    PROCEDURE_PLOT_VELOCITY = "motor1_speed"
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
        self._parser = DataParserString.from_JSON(PARSER_CONFIG_FILE)
        self._parser.set_prefix(self._protocol.ACK)
        self._parser.set_postfix(self._protocol.EOL)
        self._continous_nack_counter = 0

        # Tabs
        experiment_tab = self._experiment_tab()
        service_tab = self._service_widget()

        self.addTab(experiment_tab, "Experiment")
        self.addTab(service_tab, "Service")

        # Data logger
        self._data_logger = DataLogger(self._parser)

        # Data update timer
        self._data_update_timer = QTimer()
        self._data_update_timer.timeout.connect(self._on_update_data_timer)

    def start_data_update(self) -> None:
        """Starts the data update timer"""
        self._data_update_timer.start(self.DATA_UPDATE_INTERVAL)
        # pass

    def stop_data_update(self) -> None:
        """Stops the data update timer"""
        self._data_update_timer.stop()

    def _experiment_tab(self) -> QWidget:
        """Experiment widget

        Returns:
            QWidget: Experiment widget
        """
        self._procedures = ProceduresWidget(PROCEDURES_CONFIG_FILE)
        self._procedures.start_procedure_clicked.connect(self._on_start_procedure)
        self._procedures.stop_procedure_clicked.connect(self._on_stop_procedure)

        self._cameras = QCameraApp()
        self._cameras.enable_cameras()
        QThread.sleep(3)  # a delay to allow the cameras to start
        self._cameras.start_cameras()

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
        layout.addWidget(self._procedures, 0, 0, 1, 1)
        layout.addWidget(self._cameras, 1, 0, 1, 1)
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
        self._protocol.write(self.READ_DATA_COMMAND)
        response = self._protocol.read_raw_until_response()
        if response:
            response = response.decode().strip()
        else:
            response = ""

        if response.startswith(self._protocol.ACK):
            return_response = response
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
        """Checks the NACK counter and shows a message box if the limit is reached"""
        if self._continous_nack_counter > self.NACK_COUNTER_LIMIT:
            self._continous_nack_counter = 0
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText(
                "Failed to read data - NACK received - check the data_read command!!!"
            )
            msg_box.setWindowTitle("Error")
            msg_box.exec()

    def _update_live_velocity(self, data: dict) -> None:
        """Updates the live velocity data

        Args:
            time (float): Time
            data (dict): Data dictionary
        """
        if not self._procedures.is_procedure_running():
            return False

        time = data.get(self.PROCEDURE_PLOT_TIME, None)
        velocity = data.get(self.PROCEDURE_PLOT_VELOCITY, None)

        if time is not None and velocity is not None:
            self._procedures.append_live_data(float(velocity), float(time))

    def _on_update_data_timer(self) -> None:
        """Routine to read the data from the device and update the widgets"""
        if self.isHidden():
            return

        data = self._read_data()
        if data:
            data_dict = self._parser.parse(data)
            self._update_widgets(data_dict)
            self._data_logger.add_data(data_dict)
            self._update_live_velocity(data_dict)

            self._continous_nack_counter = 0
        else:
            self._continous_nack_counter += 1
            self._check_nack_counter()

    def _start_procedure_data_logging(self, procedure: ProcedureParameters) -> None:
        """Starts the data logging"""
        self._data_logger.create_procedure_logger(procedure.name)

        if not self._data_logger.procedure_folder:
            raise RuntimeError("Failed to create a procedure logger")

        self._cameras.change_output_dir(self._data_logger.procedure_folder)
        procedure.to_csv(self._data_logger.procedure_profile_file)

        self._cameras.start_video_recording()

    def _stop_procedure_data_logging(self) -> None:
        """Stops the data logging"""
        self._data_logger.remove_procedure_logger()
        self._cameras.stop_video_recording()
        self._cameras.stop_cameras_streaming()

    def _on_start_procedure(self) -> None:
        """Starts the procedure"""
        procedure = self._procedures.get_procedure_parameters()
        self._start_procedure_data_logging(procedure)

        try:
            args = procedure.procedure_profile_args()
            self._protocol.write_command(self.PROCEDURE_START_COMMAND, *args)
        except Exception as e:
            self._stop_procedure_data_logging()
            self._procedures.toggle_procedure_button()
            raise e

    def _on_stop_procedure(self) -> None:
        """Stops the procedure"""
        self._stop_procedure_data_logging()
        self._protocol.write_command(self.PROCEDURE_STOP_COMMAND)

    def close(self):
        self._cameras.stop_cameras_streaming()
        self._cameras.stop_cameras()
        self._cameras.quit()
        self.hide()
