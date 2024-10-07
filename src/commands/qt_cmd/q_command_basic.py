import logging
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from src.commands.qt_args.q_arg_basic import (
    QArgBasic,
)

logger = logging.getLogger("qt_commands")


class QCmdBasic(QWidget):
    DEFULT_COLUMNS_NB = 5
    send_clicked = Signal(str)

    def __init__(
        self,
        name: str,
        args: list[QArgBasic] = None,
        columns_nb: int = None,
    ) -> None:
        """Create a new QCmdBasic

        Args:
            name (str): command name
            args (list[QArgBasic], optional): arguments. Defaults to None.
            columns_nb (int, optional): number of columns in widget. Defaults to None.
        """
        super().__init__()
        self._name = name
        self._args = args or []

        columns_nb = columns_nb or self.DEFULT_COLUMNS_NB

        self._create_gui(columns_nb)

    def _create_gui(self, columns_nb: int) -> None:
        """Create the GUI

        Args:
            columns_nb (int): number of columns in widget

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError("Method not implemented")

    @property
    def name(self) -> str:
        """Get the command name

        Returns:
            str: command name
        """
        return self._name
