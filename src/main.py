import sys
import logging
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from src.app.cameras_app import QCameraApp
from src.app.com.macus_widget import MacusWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QVBoxLayout()
        self.cameras = QCameraApp()
        # layout.addWidget(self.cameras)
        self.macus_widget = MacusWidget()
        self.macus_widget.settings_box.setFixedWidth(200)
        self.macus_widget.setFixedSize(600, 200)
        layout.addWidget(self.macus_widget)

        self.setFixedSize(self.sizeHint())
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
