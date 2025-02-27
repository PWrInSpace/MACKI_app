import logging
from typing import Any
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

logger = logging.getLogger("data_text")


class DataTextBasic(QWidget):
    def __init__(self, name: str) -> None:
        """Initialize the DataTextLabel class.

        Args:
            name (str, optional): The name of the label. Defaults to "".
            text (str, optional): The text to be displayed. Defaults to "".
        """
        super().__init__()

        self._name = name
        self._init_ui()

    def _init_ui(self) -> None:
        name = self._name.capitalize().replace("_", " ")
        name_label = QLabel(name)
        self._value_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout()
        layout.addWidget(name_label)
        layout.addWidget(self._value_label)

        # FIXME: replace hardoced size with somthing auto adjustable
        name_label.setFixedWidth(100)
        self._value_label.setFixedWidth(75)

        self.setLayout(layout)

    def update_data(self, value: Any) -> None:
        """Update the data displayed in the label.

        Args:
            value (Any): The value to be displayed.
            It can be any type of data, but it has to
            be able to be converted to a string.
        """
        if isinstance(value, float):
            value_str = f"{value:.2f}"
        else:
            value_str = str(value)

        self._value_label.setText(value_str)

    @property
    def name(self) -> str:
        return self._name
