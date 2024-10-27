from typing import override
from enum import Enum

from PySide6.QtCore import Signal
from src.commands.qt_cmd.q_lock_command import QLockCmd


class ProcedureCmdState(Enum):
    RUNNING = (0,)
    IDLE = (1,)


class ProcedureCmd(QLockCmd):
    BUTTON_TXT_START = "Start"
    BUTTON_TXT_STOP = "Stop"
    BUTTON_START_STYLE = "background-color: lime; color: black"
    BUTTON_STOP_STYLE = "background-color: red; color: black"
    BUTTON_DISABLED_STYLE = "background-color: grey"
    start_clicked = Signal()
    stop_clicked = Signal()

    @override
    def __init__(self, name: str, columns_nb: int) -> None:
        super().__init__(name, columns_nb)
        self._procedures_state = ProcedureCmdState.IDLE

    @override
    def _create_gui(self, columns_nb) -> None:
        super()._create_gui(columns_nb)
        self._send_button.setText(self.BUTTON_TXT_START)
        self._send_button.setStyleSheet(self.BUTTON_DISABLED_STYLE)

        # disconnect the previous connection
        self._send_button.clicked.disconnect(self._send_button_clicked)
        self._send_button.clicked.connect(self._on_procedure_button_clicked)

    @override
    def _on_unlock_timer_timeout(self):
        if self._procedures_state != ProcedureCmdState.RUNNING:
            super()._on_unlock_timer_timeout()

    @override
    def _send_lock_stage_changed(self):
        super()._send_lock_stage_changed()

        if self._send_button.isEnabled():
            self._send_button.setStyleSheet(self.BUTTON_START_STYLE)
        else:
            self._send_button.setStyleSheet(self.BUTTON_DISABLED_STYLE)

    def _on_procedure_button_clicked(self):
        if self._procedures_state == ProcedureCmdState.IDLE:
            self._procedures_state = ProcedureCmdState.RUNNING
            self._send_button.setText(self.BUTTON_TXT_STOP)
            self._send_button.setStyleSheet(self.BUTTON_STOP_STYLE)
            self._send_lock_widget.setEnabled(False)
            self.start_clicked.emit()
        else:
            self._procedures_state = ProcedureCmdState.IDLE
            self._send_button.setText(self.BUTTON_TXT_START)
            self._send_button.setStyleSheet(self.BUTTON_START_STYLE)
            self._send_lock_widget.setChecked(False)
            self._send_lock_widget.setEnabled(True)
            self.stop_clicked.emit()

    def is_running(self) -> bool:
        return self._procedures_state == ProcedureCmdState.RUNNING
