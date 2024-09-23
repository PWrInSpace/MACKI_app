import logging
from PySide6.QtWidgets import QWidget

logger = logging.getLogger("arg")


class QArgBasic(QWidget):
    def __init__(self, name: str, description: str = None) -> None:
        super().__init__()
        self._name = name
        self._description = description or ""

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI for the argument

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError("Method not implemented")

    def get_value_str(self) -> str:
        """Get the value of the argument as a string

        Raises:
            NotImplementedError: Method not implemented

        Returns:
            str: value of the argument as a string
        """
        raise NotImplementedError("Method not implemented")

    def get_full_description(self) -> str:
        """Get the full description of the argument
        It contains name, description and other properties of the argument

        Returns:
            str: description of the argument
        """
        description = self._name.upper() + ":\n" + self._description.capitalize()
        return description

    @property
    def name(self) -> str:
        """Get the name of the argument

        Returns:
            str: name of the argument
        """
        return self._name

    @property
    def description(self) -> str:
        """Get the description of the argument

        Returns:
            str: description of the argument
        """
        return self._description
