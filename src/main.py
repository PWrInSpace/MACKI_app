import sys
# from PySide6.QtGui import QGuiApplication
# from PySide6.QtQml import QQmlApplicationEngine
# from PySide6.QtCore import QObject, Signal, QTimer

# from time import strftime, localtime

# app = QGuiApplication(sys.argv)

# engine = QQmlApplicationEngine()
# engine.quit.connect(app.quit)
# engine.load('src/main.qml')

# class Backend(QObject):

#     updated = Signal(str, arguments=['time'])
#     transmited = Signal(str, arguments=['message'])

#     def __init__(self):
#         super().__init__()

#         # Define timer.
#         self.timer = QTimer()
#         self.timer.setInterval(100)  # msecs 100 = 1/10th sec
#         self.timer.timeout.connect(self.update_time)
#         self.timer.start()

#     def update_time(self):
#         # Pass the current time to QML.
#         curr_time = strftime("%H:%M:%S", localtime())
#         self.updated.emit(curr_time)
#         self.transmited.emit("Hello from Python!")


# backend = Backend()
# # Pass the current time to QML.
# curr_time = strftime("%H:%M:%S", localtime())
# engine.rootObjects()[0].setProperty('backend', backend)

# sys.exit(app.exec())



# from src.cameras.frames_handler import FramesHandler
from src.cameras.cameras_menager import CamerasMenager
from src.cameras.handling_elements.frame_display import FrameDisplay
# import logging
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication, QWidget

# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     # Create a Qt widget, which will be our window.
#     window = QWidget()
#     window.show()  # IMPORTANT!!!!! Windows are hidden by default.

#     # Start the event loop.
#     app.exec()
    # logging.basicConfig(level=logging.DEBUG)
    # x = FramesHandler("foo")

    # y = FrameDisplay("bar")

    # app.exec()


    # x.start()
    # QThread.sleep(2)
    # x.quit()

    # y.start()
    # QThread.sleep(5)
    # y.stop()

import sys
import logging
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Open!")
        button.clicked.connect(self.on_button_click)

        button_close = QPushButton("Close!")
        button_close.clicked.connect(self.close_button)

        layout = QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(button_close)

        widget = QWidget()
        widget.setLayout(layout)

        # Set the central widget of the Window.
        self.setCentralWidget(widget)
        # self.setLayout(layout)

        self.cameras = CamerasMenager()
        self.cameras.start()

    def on_button_click(self):
        self.frame_display = FrameDisplay("bar")
        self.frame_display.start()
        # QThread.sleep(5)
        # self.frame_display.stop()

    def close_button(self):
        self.frame_display.stop()

    def closeEvent(self, event):
        self.cameras.quit()
        event.accept()

logging.basicConfig(level=logging.DEBUG)

app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()



