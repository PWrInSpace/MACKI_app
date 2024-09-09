from PySide6.QtWidgets import QAbstractSpinBox, QDoubleSpinBox
from src.commands.qt_args.q_arg_value import QArgValue


class QArgFloat(QArgValue):
    ALLOWED_TYPES = (type(None), float, int)

    def __init__(
        self,
        name: str,
        default_value: float = 0,
        min_value: float | None = None,
        max_value: float | None = None,
        unit: str = "",
        description: str = None,
    ) -> None:
        """Create a new QArgFloat

        Args:
            name (str): argument name
            default_value (float, optional): arg default value. Defaults to 0.
            min_value (float | None, optional): arg min value. Defaults to None.
            max_value (float | None, optional): arg max value. Defaults to None.
            unit (str, optional): arg unit. Defaults to "".
            description (str, optional): arg description. Defaults to None.
        """
        super().__init__(name, default_value, min_value, max_value, unit, description)

    def _check_type(self, value: int | float | None) -> bool:
        """Check if value is of the correct type

        Args:
            value (int | float | None): value to check

        Raises:
            ValueError: Value is not of the correct type

        Returns:
            bool: True if value is of the correct type
        """
        if not isinstance(value, self.ALLOWED_TYPES):
            raise ValueError(f"Value {value} is not of type {self.ALLOWED_TYPES}")

    def _create_spin_box(self) -> QAbstractSpinBox:
        """Create a new QDoubleSpinBox that is used to create the widget

        Returns:
            QAbstractSpinBox: new QDoubleSpinBox
        """
        return QDoubleSpinBox()
