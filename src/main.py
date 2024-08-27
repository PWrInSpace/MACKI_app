import sys
import logging
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from src.cameras.q_cameras_menager import QCamerasMenager

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QVBoxLayout()
        self.cameras = QCamerasMenager()
        layout.addWidget(self.cameras)
        button = QPushButton("Start Cameras")
        button.clicked.connect(self.on_button_click)
        layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.cameras.enable_cameras()

    def on_button_click(self):
        self.cameras.start_cameras()

    def close_button(self):
        self.frame_display.stop()
        self.frame_display2.stop()
        self.video_writer.stop()
        self.video_writer2.stop()

    def closeEvent(self, event):
        self.cameras.quit()
        event.accept()

logging.basicConfig(level=logging.DEBUG)

app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()



