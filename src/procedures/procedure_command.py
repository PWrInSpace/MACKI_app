from typing import override
from enum import Enum

from PySide6.QtCore import Signal
from src.commands.qt_cmd.q_lock_command import QLockCmd


class ProcedureCmdState(Enum):
    RUNNING = 0,
    IDLE = 1,


class ProcedureCmd(QLockCmd):
    BUTTON_TXT_START = "Start"
    BUTTON_TXT_STOP = "Stop"
    BUTON_START_STYLE = "background-color: green"
    BUTTON_STOP_STYLE = "background-color: red"
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
        self._send_button.setStyleSheet(self.BUTON_START_STYLE)

        # disconnect the previous connection
        self._send_button.clicked.disconnect(self._send_button_clicked)
        self._send_button.clicked.connect(self._on_procedure_button_clicked)

    @override
    def _on_unlock_timer_timeout(self):
        if self._procedures_state != ProcedureCmdState.RUNNING:
            super()._on_unlock_timer_timeout()

    def _on_procedure_button_clicked(self):
        if self._procedures_state == ProcedureCmdState.IDLE:
            self._procedures_state = ProcedureCmdState.RUNNING
            self._send_button.setText(self.BUTTON_TXT_STOP)
            self._send_button.setStyleSheet(self.BUTTON_STOP_STYLE)
            self.start_clicked.emit()
        else:
            self._procedures_state = ProcedureCmdState.IDLE
            self._send_button.setText(self.BUTTON_TXT_START)
            self._send_button.setStyleSheet(self.BUTON_START_STYLE)
            self._send_lock_widget.setChecked(False)
            self.stop_clicked.emit()