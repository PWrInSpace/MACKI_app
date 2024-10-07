import sys
import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(autouse=True)
def qapp():
    app = QApplication.instance()  # Check if an instance already exists
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()
