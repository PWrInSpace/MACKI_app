from typing import override
from src.commands.qt_args.q_arg_basic import QArgBasic, logger
from PySide6.QtWidgets import QComboBox, QVBoxLayout


class QArgEnum(QArgBasic):
    def __init__(
        self,
        name: str,
        enum: dict[str, str],
        default_name: str = "",
        description: str = "",
    ) -> None:
        """ArgInt class constructor, inherits from ArgBasic class"""

        self._enum = enum
        self._default_name = default_name

        if default_name not in self._enum:
            logger.warning(
                f"Default name '{default_name}' not found in enum '{self._enum}'"
                f" for argument '{name}'. Using first name in enum."
            )
            self._default_name = list(self._enum.keys())[0]

        super().__init__(name, description)

    @override
    def _init_ui(self) -> None:
        """Initialize the UI for the argument"""
        self._combo_box = QComboBox()
        self._combo_box.addItems(self._enum.keys())
        self._combo_box.setCurrentText(self._default_name)
        self._combo_box.setToolTip(self.get_full_description())

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._combo_box)
        self.setLayout(layout)

    @override
    def get_value_str(self) -> str:
        """Get the value of the argument as a string

        Raises:
            ValueError: Invalid value for argument

        Returns:
            str: value of the argument as a string
        """
        name = self._combo_box.currentText()

        if name not in self._enum:
            raise ValueError(f"Invalid name {name} for argument {self._name}")

        return str(self._enum[name])
