import os
from PySide6.QtWidgets import (
    QMainWindow,
)
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon

from src.app.com.macus_widget import MacusWidget
from src.com.serial import QSerialState
from src.app.experiment_window import ExperimentWindow


class App(QMainWindow):
    OCTOPUS_LOGO = os.path.join(os.getcwd(), "resources", "octopus.png")

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(self.OCTOPUS_LOGO))

        self._macus_widget = MacusWidget()
        self._macus_widget.settings_box.setFixedWidth(240)
        self._macus_widget.setFixedSize(700, 240)

        self._macus_widget.com_state_changed.connect(self._on_state_changed)

        self.setWindowTitle("MACKI - serial port communication")
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(self.sizeHint())

        self.setCentralWidget(self._macus_widget)

        self._experiment_window = ExperimentWindow(self._macus_widget.com_serial)

    @Slot(QSerialState)
    def _on_state_changed(self, state: QSerialState):
        match state:
            case QSerialState.CONNECTED:
                self._experiment_window.setEnabled(True)
                if self._experiment_window.isHidden():
                    self._experiment_window.show()
            case QSerialState.DISCONNECTED | QSerialState.MISSING:
                self._experiment_window.setEnabled(False)


    def closeEvent(self, event):
        self._macus_widget.quit()
        self._experiment_window.hide()
        event.accept()

