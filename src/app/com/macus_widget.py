import logging
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QPushButton,
    QGroupBox,
    QGridLayout,
    QTextEdit,
    QVBoxLayout,
)

from PySide6.QtCore import Qt, Signal, QTimer
from src.com.macus_serial import MacusSerial
from src.utils.qt.better_combo_box import BetterComboBox
from src.app.com.macus_widget_utils import MacusWidgetState

logger = logging.getLogger("macus_widget")


class MacusWidget(QWidget):
    BAUDRATES = ["115200"]
    BUTTON_CONNECT = "Connect"
    BUTTON_DISCONNECT = "Disconnect"
    TX_PREFIX = "TX: "
    RX_PREFIX = "RX: "

    connected = Signal()
    missing = Signal()
    disconencted = Signal()

    def __init__(self) -> None:
        """This method initializes the MacusWidget class
        """
        super().__init__()

        self._state = MacusWidgetState.UNKNOWN
        self._serial = MacusSerial()
        self._serial.set_rx_callback(self._add_rx_message_to_text_box)
        self._serial.set_tx_callback(self._add_tx_message_to_text_box)

        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._timer_routine)
        self._status_timer.start(1000)

        self._init_ui()

        self._change_state(MacusWidgetState.DISCONNECTED)

    def _create_settings_box(self) -> QGroupBox:
        """This method creates the settings box

        Returns:
            QGroupBox: settings box
        """
        port_label = QLabel("Port")
        self._port_combo = BetterComboBox()
        self._port_combo.addItems(self._serial.get_available_ports())
        self._port_combo.clicked.connect(self._update_availabel_ports)

        baudrate_label = QLabel("Baudrate")
        self._baudrate_combo = QComboBox()
        self._baudrate_combo.addItems(self.BAUDRATES)
        self._baudrate_combo.setCurrentIndex(0)
        self._baudrate_combo.setDisabled(True)

        horizontal_line = QLabel()
        horizontal_line.setFrameShape(QLabel.HLine)
        horizontal_line.setFrameShadow(QLabel.Sunken)

        state_prefix = QLabel("State: ")
        self._state_label = QLabel()
        self._state_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self._connect_button = QPushButton(self.BUTTON_CONNECT)
        self._connect_button.clicked.connect(self._on_connect_button_clicked)

        horizontal_line2 = QLabel()
        horizontal_line2.setFrameShape(QLabel.HLine)
        horizontal_line2.setFrameShadow(QLabel.Sunken)

        grid_layout = QGridLayout()
        grid_layout.addWidget(port_label, 0, 0, 1, 2)
        grid_layout.addWidget(self._port_combo, 1, 0, 1, 2)
        grid_layout.addWidget(baudrate_label, 2, 0, 1, 2)
        grid_layout.addWidget(self._baudrate_combo, 3, 0, 1, 2)
        # grid_layout.addWidget(horizontal_line, 4, 0, 1, 2)
        grid_layout.addWidget(self._connect_button, 5, 0, 1, 2)
        grid_layout.addWidget(horizontal_line2, 6, 0, 1, 2)
        grid_layout.addWidget(state_prefix, 7, 0, 1, 1)
        grid_layout.addWidget(self._state_label, 7, 1, 1, 1)

        settings_box = QGroupBox("Settings")
        settings_box.setLayout(grid_layout)

        return settings_box

    def _create_text_box(self) -> QGroupBox:
        """This method creates the text box

        Returns:
            QGroupBox: text box
        """
        self._text_edit = QTextEdit()
        self._text_edit.setLineWrapMode(QTextEdit.NoWrap)
        self._text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._text_edit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self._text_edit)

        box = QGroupBox("Preview")
        box.setLayout(layout)

        return box

    def _init_ui(self):
        """This method initializes the user interface"""
        self.settings_box = self._create_settings_box()
        self.text_box = self._create_text_box()

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.settings_box, 0, 0)
        grid_layout.addWidget(self.text_box, 0, 1)

        self.setLayout(grid_layout)

    def _update_availabel_ports(self):
        """This method is called when the port combo is clicked"""
        current_port = self._port_combo.currentText()
        self._port_combo.clear()
        self._port_combo.addItems(self._serial.get_available_ports())
        self._port_combo.setCurrentText(current_port)

    def _on_connect_button_clicked(self):
        """This method is called when the connect button is clicked
        FIXME: This implementation can lead to invalid button text,
        when the connection is lost outside of this widget
        """
        if self._serial.is_connected():
            self._serial.disconnect()
            self._change_state(MacusWidgetState.DISCONNECTED)
        else:
            port = self._port_combo.currentText()
            self._serial.connect(port)
            self._change_state(MacusWidgetState.CONNECTED)

    def _add_message_to_text_box(self, data: str, message_prefix: str = "") -> None:
        """This method adds a message to the text box

        Args:
            data (str): The data to add
            message_prefix (str, optional): The message prefix. Defaults to "".
        """
        if not data.endswith("\n"):
            data += "\n"

        if data.startswith(self._serial.ACK):
            self._text_edit.setTextColor(Qt.green)
        elif data.startswith(self._serial.NACK):
            self._text_edit.setTextColor(Qt.red)
        else:
            self._text_edit.setTextColor(Qt.white)

        self._text_edit.insertPlainText(message_prefix + data)

    def _add_tx_message_to_text_box(self, message: str) -> None:
        """This method adds a TX message to the text box

        Args:
            message (str): The message to add
        """
        self._add_message_to_text_box(message, self.TX_PREFIX)

    def _add_rx_message_to_text_box(self, message: str) -> None:
        """This method adds a RX message to the text box

        Args:
            message (str): The message to add
        """
        self._add_message_to_text_box(message, self.RX_PREFIX)

    def _change_state(self, state: MacusWidgetState) -> None:
        """This method changes the state

        Args:
            state (MacusWidgetState): The new state
        """
        logger.info(f"State changed from {self._state} to {state}")
        self._state = state

        match state:
            case MacusWidgetState.DISCONNECTED:
                self._connect_button.setText(self.BUTTON_CONNECT)
                self._state_label.setStyleSheet("color: red;")
                self._state_label.setText("DISCONNECTED")
                self.disconencted.emit()
            case MacusWidgetState.CONNECTED:
                self._connect_button.setText(self.BUTTON_DISCONNECT)
                self._state_label.setStyleSheet("color: #9BEC00;")
                self._state_label.setText("CONNECTED")
                self.connected.emit()
            case MacusWidgetState.MISSING:
                self._state_label.setStyleSheet("color: yellow;")
                self._state_label.setText("MISSING")
                self.missing.emit()

    def _timer_routine(self):
        """This method updates the status"""
        # update the port combo
        if not self._port_combo.pop_up_visible:
            self._update_availabel_ports()

        match self._state:
            case MacusWidgetState.CONNECTED:
                self._connected_state_routine()
            case MacusWidgetState.MISSING:
                self._missing_state_routine()

    def _connected_state_routine(self):
        """This method is called when the widget is in the connected state"""
        ports = self._serial.get_available_ports()
        current_port = self._serial.port

        if current_port not in ports:
            self._change_state(MacusWidgetState.MISSING)

    def _missing_state_routine(self):
        """This method is called when the widget is in the missing state"""
        ports = self._serial.get_available_ports()
        missing_port = self._serial.port

        if missing_port in ports:
            try:
                if self._serial.is_connected():
                    self._serial.disconnect()

                self._serial.connect(missing_port)
                self._change_state(MacusWidgetState.CONNECTED)
            except Exception as exc:
                # workaround: on error try again, sometimes the serial raises
                # an error even if the port is available, the second try should works
                logger.warning(f"Can't reconnect to the missing port: {exc}")

    @property
    def serial(self) -> MacusSerial:
        """This method returns the serial object

        Returns:
            MacusSerial: The serial object
        """
        return self._serial
