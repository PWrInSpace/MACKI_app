from typing import override
from src.commands.qt_args.q_arg_basic import QArgBasic, logger
from PySide6.QtWidgets import QVBoxLayout, QAbstractSpinBox


class QArgValue(QArgBasic):
    def __init__(
        self,
        name: str,
        default_value: int | float = 0,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        unit: str = "",
        description: str = None,
    ) -> None:
        """ArgInt class constructor, inherits from ArgBasic class

        Args:
            name (str): name of the argument
            default_value (int, optional): argument default value. Defaults to 0.
            min_value (int, optional): argument minimum value. Defaults to None.
            max_value (int, optional): argument maximum value. Defaults to None.

        Raises:
            ValueError: min_value must be less than or equal to max_value
            ValueError: default_value must be greater than or equal to min_value
            ValueError: default_value must be less than or equal to max_value
        """
        self._check_type(default_value)
        self._check_type(min_value)
        self._check_type(max_value)

        if ((min_value is not None) and (max_value is not None)) and (
            min_value > max_value
        ):
            raise ValueError("Min value must be less than or equal to max value")

        if ((min_value is not None) and (default_value is not None)) and (
            default_value < min_value
        ):
            raise ValueError("Default value must be greater than or equal to min value")

        if ((max_value is not None) and (default_value is not None)) and (
            default_value > max_value
        ):
            raise ValueError("Default value must be less than or equal to max value")

        self._default_value = default_value
        self._min_value = min_value
        self._max_value = max_value
        self._unit = f" {unit}" if unit else ""

        super().__init__(name, description)

    def _check_type(self, value: int | float) -> None:
        """Check if value is of the correct type

        Args:
            value (int): value to be checked

        Returns:
            bool: True if value is of the correct type, False otherwise
        """
        raise NotImplementedError("Methode not implemented")

    def _create_spin_box(self) -> QAbstractSpinBox:
        """Create spin box widget, that will be used to set the argument gui

        Raises:
            NotImplementedError: Method not implemented

        Returns:
            QAbstractSpinBox: spin box widget
        """
        raise NotImplementedError("Methode not implemented")

    @override
    def _init_ui(self) -> None:
        """Initialize the user interface"""
        self._spin_box = self._create_spin_box()

        if self._min_value:
            self._spin_box.setMinimum(self._min_value)

        if self._max_value:
            self._spin_box.setMaximum(self._max_value)

        if self._default_value:
            self._spin_box.setValue(self._default_value)

        if self._unit:
            self._spin_box.setSuffix(self._unit)

        self._spin_box.setToolTip(self.get_full_description())

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._spin_box)
        self.setLayout(layout)

    def check_value(self, value: int | float) -> bool:
        """Check if value is valid

        Args:
            value (int): value to be checked

        Returns:
            int: value
        """
        if (self._min_value is not None) and (value < self._min_value):
            logger.error(f"Value {value} is less than min value {self._min_value}")
            valid = False
        elif (self._max_value is not None) and (value > self._max_value):
            logger.error(f"Value {value} is greater than max value {self._max_value}")
            valid = False
        else:
            valid = True

        return valid

    @override
    def get_value_str(self) -> str:
        """Get the value of the argument as a string

        Raises:
            ValueError: Invalid value for the argument

        Returns:
            str: value of the argument as a string
        """
        value = self._spin_box.value()

        if not self.check_value(value):
            raise ValueError(f"Invalid value {value} for argument {self._name}")

        return str(value)

    @override
    def get_full_description(self) -> str:
        """Update description with min and max values"""
        description = super().get_full_description()

        if self._min_value is not None:
            description += f"\n\nMin: {self._min_value}"
        if self._max_value is not None:
            description += f"\nMax: {self._max_value}"

        return description

    @property
    def default_value(self) -> int:
        """Return default value

        Returns:
            int: default value
        """
        return self._default_value

    @property
    def min_value(self) -> int:
        """Return minimum value

        Returns:
            int: minimum value
        """
        return self._min_value

    @property
    def max_value(self) -> int:
        """Return maximum value

        Returns:
            int: maximum value
        """
        return self._max_value

    @property
    def unit(self) -> str:
        """Return unit

        Returns:
            str: unit
        """
        return self._unit
