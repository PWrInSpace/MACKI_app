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

from PySide6.QtCore import Qt, Signal
from src.com.macus_serial import MacusSerial
from src.utils.qt.better_combo_box import BetterComboBox


class MacusWidget(QWidget):
    BAUDRATES = ["115200"]
    BUTTON_CONNECT = "Connect"
    BUTTON_DISCONNECT = "Disconnect"
    TX_PREFIX = "TX: "
    RX_PREFIX = "RX: "

    connected = Signal()
    disconencted = Signal()

    def __init__(self, macus: MacusSerial) -> None:
        """This method initializes the MacusWidget class

        Args:
            macus (MacusSerial): MacusSerial instance
        """
        super().__init__()

        self._macus = macus
        self._macus.set_rx_callback(self._add_rx_message_to_text_box)
        self._macus.set_tx_callback(self._add_tx_message_to_text_box)

        self._init_ui()

    def _create_settings_box(self) -> QGroupBox:
        """This method creates the settings box

        Returns:
            QGroupBox: settings box
        """
        port_label = QLabel("Port")
        self._port_combo = BetterComboBox()
        self._port_combo.addItems(self._macus.get_available_ports())
        self._port_combo.clicked.connect(self._on_port_combo_clicked)

        baudrate_label = QLabel("Baudrate")
        self._baudrate_combo = QComboBox()
        self._baudrate_combo.addItems(self.BAUDRATES)
        self._baudrate_combo.setCurrentIndex(0)
        self._baudrate_combo.setDisabled(True)

        horizontal_line = QLabel()
        horizontal_line.setFrameShape(QLabel.HLine)
        horizontal_line.setFrameShadow(QLabel.Sunken)

        self._connect_button = QPushButton(self.BUTTON_CONNECT)
        self._connect_button.clicked.connect(self._on_connect_button_clicked)

        grid_layout = QGridLayout()
        grid_layout.addWidget(port_label, 0, 0)
        grid_layout.addWidget(self._port_combo, 1, 0)
        grid_layout.addWidget(baudrate_label, 2, 0)
        grid_layout.addWidget(self._baudrate_combo, 3, 0)
        grid_layout.addWidget(horizontal_line, 4, 0)
        grid_layout.addWidget(self._connect_button, 5, 0)

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

    def _on_port_combo_clicked(self):
        """This method is called when the port combo is clicked"""
        self._port_combo.clear()
        self._port_combo.addItems(self._macus.get_available_ports())

    def _on_connect_button_clicked(self):
        """This method is called when the connect button is clicked
        FIXME: This implementation can lead to invalid button text,
        when the connection is lost outside of this widget
        """
        if self._macus.is_connected():
            self._macus.disconnect()
            self._connect_button.setText(self.BUTTON_CONNECT)
            self.disconencted.emit()
        else:
            port = self._port_combo.currentText()
            self._macus.connect(port)
            self._connect_button.setText(self.BUTTON_DISCONNECT)
            self.connected.emit()

    def _add_message_to_text_box(self, data: str, message_prefix: str = "") -> None:
        """This method adds a message to the text box

        Args:
            data (str): The data to add
            message_prefix (str, optional): The message prefix. Defaults to "".
        """
        if not data.endswith("\n"):
            data += "\n"

        if data.startswith(self._macus.ACK):
            self._text_edit.setTextColor(Qt.green)
        elif data.startswith(self._macus.NACK):
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
