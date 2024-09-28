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

from PySide6.QtCore import Qt, QTimer, Signal
from src.com.serial import (
    QSerial,
    QSerialState,
    QSerialStateControlThread
)
from src.utils.qt.better_combo_box import BetterComboBox
from src.utils.colors import Colors

logger = logging.getLogger("macus_widget")


class MacusWidget(QWidget):
    BAUDRATES = ["115200"]
    BUTTON_CONNECT = "Connect"
    BUTTON_DISCONNECT = "Disconnect"
    TX_PREFIX = "TX: "
    RX_PREFIX = "RX: "
    PORTS_TIMER_INTERVAL_MS = 1000

    def __init__(self) -> None:
        """This method initializes the MacusWidget class"""
        super().__init__()

        self._com_serial = QSerial(baudrate=self.BAUDRATES[0])
        self._com_serial.set_rx_callback(self._add_rx_message_to_text_box)
        self._com_serial.set_tx_callback(self._add_tx_message_to_text_box)

        self._com_serial_state = QSerialStateControlThread(self._com_serial)
        self._com_serial_state.state_changed.connect(self._update_state_label)
        self._com_serial_state.start()

        self._available_ports_timer = QTimer()
        self._available_ports_timer.timeout.connect(self._timer_routine)
        self._available_ports_timer.start(self.PORTS_TIMER_INTERVAL_MS)

        self._init_ui()

    def _create_settings_box(self) -> QGroupBox:
        """This method creates the settings box

        Returns:
            QGroupBox: settings box
        """
        port_label = QLabel("Port")
        self._port_combo = BetterComboBox()
        self._port_combo.addItems(self._com_serial.get_available_ports())
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
        self._update_state_label(QSerialState.DISCONNECTED)

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
        available_ports = [port.name for port in self._com_serial.get_available_ports()]

        self._port_combo.clear()
        self._port_combo.addItems(available_ports)
        self._port_combo.setCurrentText(current_port)

    def _on_connect_button_clicked(self):
        """This method is called when the connect button is clicked
        FIXME: This implementation can lead to invalid button text,
        when the connection is lost outside of this widget
        """
        if self._com_serial.is_connected():
            self._com_serial.disconnect()
            self._connect_button.setText(self.BUTTON_CONNECT)
        else:
            port = self._port_combo.currentText()
            self._com_serial.connect(port)
            self._connect_button.setText(self.BUTTON_DISCONNECT)

    def _update_state_label(self, state: QSerialState):
        """This method updates the state label

        Args:
            state (str): The state
        """
        match state:
            case QSerialState.CONNECTED:
                color = Colors.GREEN
            case QSerialState.DISCONNECTED:
                color = Colors.RED
            case QSerialState.MISSING:
                color = Colors.YELLOW
            case _:
                color = Colors.WHITE

        self._state_label.setText(state.name)
        self._state_label.setStyleSheet(f"color: {color.value};")

    def _add_message_to_text_box(self, data: str, message_prefix: str = "") -> None:
        """This method adds a message to the text box

        Args:
            data (str): The data to add
            message_prefix (str, optional): The message prefix. Defaults to "".
        """
        if not data.endswith("\n"):
            data += "\n"

        if data.startswith(self._com_serial.ACK):
            self._text_edit.setTextColor(Qt.green)
        elif data.startswith(self._com_serial.NACK):
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

    def _timer_routine(self):
        """This method updates the status"""
        # update the port combo
        if not self._port_combo.is_pop_up_visible():
            self._update_availabel_ports()

    def quit(self):
        """This method stops the threads"""
        if self._com_serial.is_connected():
            self._com_serial.disconnect()

        self._com_serial_state.terminate()
        self._com_serial_state.wait()  # wait a litle bit for the thread to finish

        self._available_ports_timer.stop()

    @property
    def com_serial(self) -> QSerial:
        """This method returns the serial object

        Returns:
            MacusSerial: The serial object
        """
        return self._com_serial

    @property
    def com_state_changed(self) -> Signal:
        """This method returns the serial state object

        Returns:
            MacusSerialState: The serial state object
        """
        return self._com_serial_state.state_changed
