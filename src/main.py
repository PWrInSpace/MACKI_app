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
from src.data_displays import (
    DataDisplayText,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout()
        self.cameras = QCameraApp()
        # layout.addWidget(self.cameras)

        # self.macus_widget = MacusWidget()
        # self.macus_widget.settings_box.setFixedWidth(240)
        # self.macus_widget.setFixedSize(700, 240)
        # layout.addWidget(self.macus_widget)
        self.data_display = DataDisplayText.from_JSON("config/data_text.json")
        data = {
            "title": 32,
            "pressure": 0,
            "valve_state": "1",
        }
        self.data_display.update_data(data)
        layout.addWidget(self.data_display)

        widget = QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        self.setFixedSize(self.sizeHint())
        self.setCentralWidget(widget)
        self.cameras.enable_cameras()

    def closeEvent(self, event):
        self.cameras.terminate_threads()
        # self.macus_widget.quit()
        event.accept()


logging.basicConfig(level=logging.INFO)


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
