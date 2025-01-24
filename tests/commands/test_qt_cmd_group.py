import pytest
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from src.commands import QCmdGroup
from src.commands.qt_cmd import QSerialCmd, QLockCmd
from src.commands.qt_args import QArgInt, QArgFloat, QArgEnum
from tests.communication.com_mock import ComMock

GROUP_NAME = "test_cmd_group"


@pytest.fixture
def commands():
    args = [
        QArgInt("test_arg_1", 0, 0, 100),
        QArgFloat("test_arg_2", 0, 0.0, 100.0),
        QArgEnum("test_arg_3", {"option_1": 1, "option_2": 2, "option_3": 3}),
    ]

    commands = [
        QSerialCmd("test_cmd_1", args),
        QSerialCmd("test_cmd_2", args),
        QSerialCmd("test_cmd_3", args),
    ]

    return commands


@pytest.fixture
def protocol():
    return ComMock()


@pytest.fixture
def cmd_group(commands, protocol):
    return QCmdGroup("test_cmd_group", commands, protocol)


def test_init(cmd_group, commands, protocol):
    assert cmd_group._name == GROUP_NAME
    assert cmd_group._commands == commands
    assert cmd_group._protocol is protocol


def test_change_protocol(cmd_group, protocol):
    assert cmd_group._protocol is protocol

    cmd_group.set_protocol(None)
    assert cmd_group._protocol is None


def test_init_ui(cmd_group):
    layout = cmd_group.layout()
    assert layout.count() == 3

    assert isinstance(layout.itemAt(0).widget(), QSerialCmd)
    assert isinstance(layout.itemAt(1).widget(), QSerialCmd)
    assert isinstance(layout.itemAt(2).widget(), QSerialCmd)


def test_send_clicked(cmd_group, protocol):
    layout = cmd_group.layout()

    for i in range(layout.count()):
        cmd_widget = layout.itemAt(i).widget()

        QTest.mouseClick(cmd_widget._send_button, Qt.MouseButton.LeftButton)

        command = cmd_widget._create_command_str()

        assert protocol.last_write == command
        assert protocol.write_count == i + 1


def test_send_clicked_without_protocol(cmd_group, protocol):
    cmd_group.set_protocol(None)
    layout = cmd_group.layout()

    for i in range(layout.count()):
        cmd_widget = layout.itemAt(i).widget()

        QTest.mouseClick(cmd_widget._send_button, Qt.MouseButton.LeftButton)

        assert protocol.last_write is None
        assert protocol.write_count == 0


def test_from_JSON(protocol):
    cmd_group = QCmdGroup.from_JSON("tests/commands/test.json", protocol)

    assert cmd_group._name == "test"
    assert cmd_group._protocol is protocol
    assert len(cmd_group._commands) == 3

    layout = cmd_group.layout()
    assert layout.count() == 3

    first_command = layout.itemAt(0).widget()
    second_command = layout.itemAt(1).widget()
    third_command = layout.itemAt(2).widget()

    assert isinstance(first_command, QSerialCmd)
    assert first_command._name == "test_cmd_1"

    assert isinstance(second_command, QSerialCmd)
    assert second_command._name == "test_cmd_2"

    assert isinstance(third_command, QLockCmd)
    assert third_command._name == "test_cmd_3"

    first_command_args = first_command._args
    first_cmd_first_arg = first_command_args[0]
    assert isinstance(first_cmd_first_arg, QArgInt)
    assert first_cmd_first_arg.name == "cmd1_arg1"
    assert first_cmd_first_arg.default_value == 0
    assert first_cmd_first_arg.min_value == 0
    assert first_cmd_first_arg.max_value == 10
    assert first_cmd_first_arg.unit == " g"
    assert first_cmd_first_arg.description == "First argument"

    first_cmd_second_arg = first_command_args[1]
    assert isinstance(first_cmd_second_arg, QArgEnum)
    assert first_cmd_second_arg.name == "cmd1_arg2"
    assert first_cmd_second_arg._default_name == "test2"
    assert first_cmd_second_arg._enum == {"test": 0, "test2": 1, "test3": 2}
    assert first_cmd_second_arg.description == "Second argument"

    second_command_args = second_command._args
    second_cmd_first_arg = second_command_args[0]
    assert isinstance(second_cmd_first_arg, QArgInt)
    assert second_cmd_first_arg.name == "cmd2_arg1"
    assert second_cmd_first_arg.default_value == 0
    assert second_cmd_first_arg.min_value == 0
    assert second_cmd_first_arg.max_value == 10
    assert second_cmd_first_arg.unit == " g"
    assert second_cmd_first_arg.description == "First argument"

    second_cmd_second_arg = second_command_args[1]
    assert isinstance(second_cmd_second_arg, QArgFloat)
    assert second_cmd_second_arg.name == "cmd2_arg2"
    assert second_cmd_second_arg.default_value == 0
    assert second_cmd_second_arg.min_value == 0
    assert second_cmd_second_arg.max_value == 10
    assert second_cmd_second_arg.unit == " g"
    assert second_cmd_second_arg.description == "Second argument"

    third_command_args = third_command._args
    assert third_command_args == []


# TBD IN THE FUTURE
# def test_from_JSON_app_files(protocol):
#     with does_not_raise():
