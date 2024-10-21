import json
import logging
from typing import Self
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGroupBox, QVBoxLayout

from src.com.abstract import ComProtoBasic
from src.commands.qt_cmd import (
    QCmdBasic,
    QSerialCmd,
    QLockCmd,
)
from src.commands.qt_args import QArgInt, QArgFloat, QArgEnum, QArgBasic

logger = logging.getLogger(__name__)


class QCmdGroup(QGroupBox):
    def __init__(
        self,
        name: str,
        commands: QCmdBasic,
        protocol: ComProtoBasic | None = None,
    ) -> None:
        """Create a new QCmdGroup

        Args:
            name (str): group name
            commands (QCmdBasic): commands
            protocol (ComProtoBasic | None, optional): communication protocol.
            Defaults to None.
        """
        super().__init__(name)
        self._name = name
        self._commands = commands
        self._protocol = protocol

        self._init_ui()

    def set_protocol(self, protocol: ComProtoBasic) -> None:
        """Set the communication protocol

        Args:
            protocol (ComProtoBasic): communication protocol
        """
        self._protocol = protocol

    def _init_ui(self) -> None:
        """Initialize the user interface"""
        layout = QVBoxLayout()

        for command in self._commands:
            layout.addWidget(command)
            command.send_clicked.connect(self._on_send_clicked)

        self.setLayout(layout)

    @Slot(str)
    def _on_send_clicked(self, message: str) -> None:
        """Called when a command send button was clicked

        Args:
            message (str): message to be sent
        """
        if self._protocol is not None:
            self._protocol.write_and_check(message)

    @staticmethod
    def from_JSON(file: str, protocol: ComProtoBasic) -> Self:
        """Create a QCmdGroup from a JSON file

        Args:
            file (str): path to JSON file
            protocol (ComProtoBasic): communication protocol

        Returns:
            Self: QCmdGroup
        """
        with open(file, "r") as f:
            obj = json.loads(f.read(), cls=_JSON_decoder)

        obj.set_protocol(protocol)
        return obj


# To avoid circural imports, this class is defined in this file
class _JSON_decoder(json.JSONDecoder):
    """JSON decoder for QCmdGroup

    Args:
        json: JSON decoder
    """

    def __init__(self):
        """Create a new JSON decoder"""
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_arg(self, d: dict) -> QArgBasic:
        """Convert a dictionary to an argument

        Args:
            d (dict): dictionary to convert

        Raises:
            ValueError: Invalid argument type

        Returns:
            Any: argument
        """
        arg_type = d.pop("arg_type")
        if arg_type == "QArgInt":
            return QArgInt(**d)
        elif arg_type == "QArgFloat":
            return QArgFloat(**d)
        elif arg_type == "QArgEnum":
            return QArgEnum(**d)
        else:
            raise ValueError(f"Invalid argument type: {arg_type}")

    def dict_to_command(self, d) -> QCmdBasic:
        """Convert a dictionary to a command

        Args:
            d (dict): dictionary to convert

        Raises:
            ValueError: Invalid command type

        Returns:
            QCmdBasic: command
        """
        cmd_type = d.pop("cmd_type")
        if cmd_type == "QSerialCmd":
            return QSerialCmd(**d)
        elif cmd_type == "QLockCmd":
            return QLockCmd(**d)
        else:
            raise ValueError(f"Invalid command type: {cmd_type}")

    def dict_to_group(self, d) -> QCmdGroup:
        """Convert a dictionary to a group

        Args:
            d (dict): dictionary to convert

        Returns:
            QCmdGroup: group
        """
        commands = []
        for command in d["commands"]:
            command["columns_nb"] = d["max_columns_nb"]
            commands.append(self.dict_to_command(command))

        return QCmdGroup(d["group_name"], commands, None)

    def dict_to_object(self, d) -> QCmdGroup:
        """Convert a dictionary to an object

        Args:
            d (dict): dictionary to convert

        Returns:
            QCmdGroup: group
        """
        if "arg_type" in d:
            return self.dict_to_arg(d)
        elif "cmd_type" in d:
            # not convert to command, because we want to
            # calculate the max number of arguments in commands
            # to adjust the arg grid
            return d
        elif "group_name" in d:
            return self.dict_to_group(d)

        return d
