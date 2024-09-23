from PySide6.QtWidgets import QAbstractSpinBox, QSpinBox
from src.commands.qt_args.q_arg_value import QArgValue


class QArgInt(QArgValue):
    ALLOWED_TYPES = (type(None), int)

    def __init__(
        self,
        name: str,
        default_value: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
        unit: str = "",
        description: str = None,
    ) -> None:
        """Create a new QArgInt

        Args:
            name (str): argument name
            default_value (int, optional): arg default name. Defaults to 0.
            min_value (int | None, optional): arg min value. Defaults to None.
            max_value (int | None, optional): arg max value. Defaults to None.
            unit (str, optional): arg unit. Defaults to "".
            description (str, optional): arg description. Defaults to None.
        """
        super().__init__(name, default_value, min_value, max_value, unit, description)

    def _create_spin_box(self) -> QAbstractSpinBox:
        """Create a new QSpinBox that is used to create the widget

        Returns:
            QAbstractSpinBox: new QSpinBox
        """
        return QSpinBox()
