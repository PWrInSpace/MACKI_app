import sys
import logging
from PySide6.QtWidgets import QApplication

from src.app.app import App


def main():
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)

    window = App()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()