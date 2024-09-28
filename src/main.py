import sys
import logging
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from src.app.cameras_app import QCameraApp
from src.data_displays import (
    DataDisplayText,
    DataDisplayPlot,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout()
        self.cameras = QCameraApp()

        self.data_display_text = DataDisplayText.from_JSON("config/data_text.json")
        data = {
            "title": 32,
            "pressure": 0,
            "valve_state": "1",
        }
        self.data_display_text.update_data(data)

        self.data_display_plot = DataDisplayPlot.from_JSON("config/data_plot.json")

        data = {"pressure": 0, "temperature": 0, "time": 0}
        self.data_display_plot.update_data(data)

        data = {"pressure": 1, "temperature": 1, "time": 1}
        self.data_display_plot.update_data(data)

        layout = QVBoxLayout()
        layout.addWidget(self.data_display_plot)
        layout.addWidget(self.data_display_text)

        widget = QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # self.setFixedSize(self.sizeHint())
        # self.setFixedSize(self.sizeHint())
        self.setCentralWidget(widget)
        # self.cameras.enable_cameras()

    def closeEvent(self, event):
        self.cameras.terminate_threads()
        # self.macus_widget.quit()
        event.accept()


logging.basicConfig(level=logging.INFO)


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
