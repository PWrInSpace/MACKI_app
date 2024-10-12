from PySide6.QtWidgets import (
    QMainWindow,
)
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon

from src.app.config import OCTOPUS_SERIAL_WIN
from src.app.com.macus_widget import MacusWidget
from src.com.serial import QSerialState
from src.app.experiment_window import ExperimentWindow
from src.procedures.procedures_widget import ProceduresWidget


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(OCTOPUS_SERIAL_WIN))

        self._macus_widget = MacusWidget()
        self._macus_widget.settings_box.setFixedWidth(250)
        self._macus_widget.setFixedSize(700, 250)

        self._macus_widget.com_state_changed.connect(self._on_state_changed)

        self.setWindowTitle("MACKI - serial port communication")
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(self.sizeHint())

        # procedure = ProceduresWidget(self._macus_widget.com_serial)
        # self.setCentralWidget(procedure)
        self.setCentralWidget(self._macus_widget)

        self._experiment_window = ExperimentWindow(self._macus_widget.com_serial)
        self._experiment_window.setMinimumWidth(1400)

    @Slot(QSerialState)
    def _on_state_changed(self, state: QSerialState):
        match state:
            case QSerialState.CONNECTED:
                self._experiment_window.start_data_update()
                self._experiment_window.setEnabled(True)
                if self._experiment_window.isHidden():
                    self._experiment_window.show()

            case QSerialState.DISCONNECTED | QSerialState.MISSING:
                self._experiment_window.setEnabled(False)
                self._experiment_window.stop_data_update()

            case _:
                raise RuntimeError(f"Unknown state: {state}")

    def closeEvent(self, event):
        self._macus_widget.quit()
        self._experiment_window.hide()
        event.accept()
