import sys
import logging

from PySide6.QtWidgets import QApplication
from src.app.app import App
from PySide6.QtWidgets import QMessageBox


def excepthook(exc_type, exc_value, exc_traceback):
    error_message = f"Exception type: {exc_type.__name__}\nException value: {exc_value}"
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText("An unexpected error occurred")
    msg_box.setInformativeText(error_message)
    msg_box.setWindowTitle("Error")
    msg_box.exec()


def main():
    sys.excepthook = excepthook
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)

    with open("resources/theme.qss") as f:
        app.setStyleSheet(f.read())

    window = App()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
