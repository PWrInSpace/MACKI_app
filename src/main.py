import sys
import logging
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from src.cameras.q_cameras_menager import QCamerasMenager

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QVBoxLayout()
        self.cameras = QCamerasMenager()
        layout.addWidget(self.cameras)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def on_button_click(self):
        self.video_writer.start()
        self.video_writer2.start()
        self.frame_display.start()
        self.frame_display2.start()

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



