from typing import override
from PySide6.QtWidgets import QLabel, QPushButton

from src.utils.qt import QSerialCmdLay
from src.commands.qt_cmd.q_command_basic import QCmdBasic, logger
from src.commands.qt_args.q_arg_basic import QArgBasic


class QSerialCmd(QCmdBasic):
    COMMAND_EOF = "\n\r"
    SEND_BUTTON_TEXT = "Send"

    def __init__(
        self, name: str, args: list[QArgBasic], columns_nb: int = None
    ) -> None:
        """Create a new QSerialCmd

        Args:
            name (str): command name
            args (list[QArgBasic]): arguments
            columns_nb (int, optional): number of columns in widget. Defaults to None.
        """
        super().__init__(name, args, columns_nb)

    @override
    def _create_gui(self, columns_nb: int) -> None:
        """Create the GUI

        Args:
            columns_nb (int): number of columns in widget
        """
        name_label = QLabel(self._name)
        self._send_button = QPushButton(self.SEND_BUTTON_TEXT)
        self._send_button.clicked.connect(self._send_button_clicked)

        layout = QSerialCmdLay(columns_nb)
        layout.addWidgetBeforeArgs(name_label)
        layout.addArgWidgets(self._args)
        layout.addLastWidget(self._send_button)
        layout.setColumnStretch()

        self.setLayout(layout)

    def _create_command_str(self) -> str:
        """Create the command string

        Returns:
            str: command string
        """
        command_str = self._name

        for arg_widget in self._args:
            # get_value_str method checks if the value is valid
            command_str += " " + arg_widget.get_value_str()

        return command_str + self.COMMAND_EOF

    def _send_button_clicked(self) -> None:
        """Called when the send button is clicked"""
        command_str = self._create_command_str()
        self.send_clicked.emit(command_str)
        logger.info(
            f"Send button clicked for command {self._name}, "
            f"sending message: {command_str.strip()}"
        )
