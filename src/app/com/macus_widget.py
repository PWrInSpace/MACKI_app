from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QPushButton,
    QGroupBox,
    QGridLayout
)
from PySide6.QtCore import Signal, QTimer

from src.com.macus_serial import MacusSerial


class MacusWidget(QWidget, MacusSerial):
    STATUS_TIMER_TIMEOUT_MS = 1000
    BAUDRATES = ["115200"]

    def __init__(self) -> None:
        QWidget.__init__(self)
        MacusSerial.__init__(self)

        # self._serial = MacusSerial()
        self._status_timer = QTimer()
        # self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(self.STATUS_TIMER_TIMEOUT_MS)

        self._init_ui()

    def _create_settings_box(self):
        port_label = QLabel("Port")
        self._port_combo = QComboBox()
        self._port_combo.addItems(self.get_available_ports())

        baudrate_label = QLabel("Baudrate")
        self._baudrate_combo = QComboBox()
        self._baudrate_combo.addItems(self.BAUDRATES)
        self._baudrate_combo.setCurrentIndex(0)
        self._baudrate_combo.setDisabled(True)

        self._connect_button = QPushButton("Connect")
        # self._connect_button.clicked.connect(self._on_connect_button_clicked)

        grid_layout = QGridLayout()
        grid_layout.addWidget(port_label, 0, 0)
        grid_layout.addWidget(self._port_combo, 1, 0)
        grid_layout.addWidget(baudrate_label, 2, 0)
        grid_layout.addWidget(self._baudrate_combo, 3, 0)
        grid_layout.addWidget(self._connect_button, 4, 0)

        settings_box = QGroupBox("Settings")
        settings_box.setLayout(grid_layout)

        return settings_box

    def _init_ui(self):
        settings_box = self._create_settings_box()

        grid_layout = QGridLayout()
        grid_layout.addWidget(settings_box, 0, 0)

        self.setLayout(grid_layout)