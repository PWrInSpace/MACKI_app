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
from src.data_displays import DataDisplayText, DataTextNumber, DataTextValues, Values
from src.utils.colors import Colors

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
        values = Values(["10"], ["KOX"], [Colors.MINT])
        config = [
            DataTextNumber("Test", 12, 32),
            DataTextValues("Test values", values)
        ]

        self.data_display = DataDisplayText(
            data_display_config=config,
            name="Data Display",
            col_num=2,
        )
        data = {
            "Data Display 1": 32,
            "Data Display 2": 12,
            "Test": 42,
            "Test values": 10
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
        self.macus_widget.quit()
        event.accept()


logging.basicConfig(level=logging.INFO)


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
