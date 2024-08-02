# import sys

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
