from typing import Any
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


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
        name_label = QLabel(self._name)
        self._value_label = QLabel()

        layout = QHBoxLayout()
        layout.addWidget(name_label)
        layout.addWidget(self._value_label)

        self.setLayout(layout)

    def update_data(self, value: Any) -> None:
        """Update the data displayed in the label.

        Args:
            value (Any): The value to be displayed.
            It can be any type of data, but it has to
            be able to be converted to a string.
        """
        self._value_label.setText(str(value))
