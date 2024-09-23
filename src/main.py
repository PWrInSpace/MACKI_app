import sys
import logging
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from src.app.cameras_app import QCameraApp
from src.communication import CommunicationProtocolBasic
from src.commands import QCmdGroup


class Proto(CommunicationProtocolBasic):
    def connect(self):
        print("Connected")

    def disconnect(self):
        print("Disconnected")

    def write(self, data: str):
        print("Writing", data)

    def read(self):
        print("Reading")

    def is_connected(self):
        print("Is connected")
        return True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QVBoxLayout()
        self.cameras = QCameraApp()

        proto = Proto()
        group = QCmdGroup.from_JSON("test.json", proto)

        layout.addWidget(group)
        layout.addWidget(self.cameras)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.cameras.enable_cameras()

    def closeEvent(self, event):
        self.cameras.terminate_threads()
        event.accept()


logging.basicConfig(level=logging.INFO)


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
