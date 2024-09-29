from typing import override

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QLabel, QCheckBox, QPushButton

from src.utils.qt import QSerialCmdLay
from src.commands.qt_cmd.q_serial_command import QSerialCmd
from src.commands.qt_cmd.q_command_basic import logger

# TO DO: add args test and signal argument tests

class QProcedureCmd(QSerialCmd):
    ADDITIONAL_COLUMNS_NB = 3
    LABEL_STRETCH = 1
    UNLOCK_TIMER_TIMEOUT = 5000
    LOCK_UNCHECKED = "Locked"
    LOCK_CHECKED = "Unlocked"

    unlocked = Signal(str)
    locked = Signal(str)

    def __init__(self, name: str, columns_nb: int) -> None:
        """Create a new QProcedureCmd

        Args:
            command (Command): Command to create GUI for
            protocol (CommunicationProtocolBasic): Communication protocol to use
            for sending/reading the command
        """
        super().__init__(name, None, columns_nb)
        self._args_list = []
        self._unlocked_timer = QTimer()
        self._unlocked_timer.setSingleShot(True)
        self._unlocked_timer.timeout.connect(self._on_unlock_timer_timeout)

    @override
    def _create_gui(self, columns_nb) -> None:
        """Create the GUI for the command"""
        name_label = QLabel(self._name)

        self._send_lock_widget = QCheckBox()
        self._send_lock_widget.setText(self.LOCK_UNCHECKED)
        self._send_lock_widget.stateChanged.connect(self._send_lock_stage_changed)

        self._send_button = QPushButton(self.SEND_BUTTON_TEXT)
        self._send_button.setDisabled(True)
        self._send_button.clicked.connect(self._send_button_clicked)

        layout = QSerialCmdLay(columns_nb)
        layout.addWidgetBeforeArgs(name_label)
        layout.addArgWidgets([self._send_lock_widget])
        layout.addLastWidget(self._send_button)
        layout.setColumnStretch()

        self.setLayout(layout)

    def _on_unlock_timer_timeout(self):
        """Called when unlock timer times out
        This set the lock box to unchecked
        which trigger the lock box state changed
        """
        self._send_lock_widget.setChecked(False)

    def _send_lock_stage_changed(self):
        """Called when the lock box state is changed"""
        if self._send_lock_widget.isChecked():
            self._send_lock_widget.setText(self.LOCK_CHECKED)
            self._send_button.setDisabled(False)
            self._unlocked_timer.start(self.UNLOCK_TIMER_TIMEOUT)
            self.unlocked.emit(self._name)
        else:
            self._send_lock_widget.setText(self.LOCK_UNCHECKED)
            self._send_button.setDisabled(True)
            self._unlocked_timer.stop()
            self.locked.emit(self._name)

    def set_locked(self) -> None:
        """Set the command as unlocked"""
        self._send_lock_widget.setChecked(False)

    def set_args_list(self, args_list: list[str]):
        """Set the list of arguments for the command"""
        self._args_list = args_list

    @override
    def _create_command_str(self) -> str:
        """Create the command string
        We do not have arguments to choose from, so we just send
        command with the arguments gicen in the args_list

        Returns:
            str: command string
        """
        command_str = self._name

        if self._args_list:
            command_str += " " + " ".join(self._args_list)

        return command_str + self.COMMAND_EOF

    @override
    def _send_button_clicked(self):
        """Called when the send button is clicked"""
        super()._send_button_clicked()
        self._send_lock_widget.setChecked(False)
