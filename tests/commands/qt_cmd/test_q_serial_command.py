import pytest
from PySide6.QtWidgets import QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest, QSignalSpy

from src.commands.qt_cmd import QSerialCmd
from src.commands.qt_args import QArgInt
from src.utils.qt import QSerialCmdLay

CMD_NAME = "test_cmd"
CMD_COLUMNS_NB = 5


@pytest.fixture
def args():
    args = [
        # this tests does not check each QArg, this was done in q_arg tests
        # QCommand only knows about QArgBasic, so it does not matter what QArg is used
        QArgInt("arg2", 3, 3, 12),
        QArgInt("arg1", 2, 2, 7),
    ]

    return args


@pytest.fixture
def q_serial_cmd(args):
    return QSerialCmd(CMD_NAME, args, CMD_COLUMNS_NB)


def test_init_fail():
    test = [
        QArgInt("arg2", 3, 3, 12),
        QArgInt("arg1", 2, 2, 7),
        QArgInt("arg3", 2, 2, 7),
    ]

    with pytest.raises(ValueError):
        QSerialCmd(CMD_NAME, test, 4)


def test_init_pass(q_serial_cmd, args):
    assert q_serial_cmd._name == CMD_NAME
    assert q_serial_cmd._args == args


def test_gui(q_serial_cmd, args):
    assert isinstance(q_serial_cmd.layout(), QSerialCmdLay)

    name_layout = q_serial_cmd.layout().itemAt(0).widget()
    assert isinstance(name_layout, QLabel)
    assert name_layout.text() == CMD_NAME

    first_argument = q_serial_cmd.layout().itemAt(1).widget()
    second_argument = q_serial_cmd.layout().itemAt(2).widget()
    assert first_argument == args[0]
    assert second_argument == args[1]

    send_button = q_serial_cmd._send_button
    assert isinstance(send_button, QPushButton)
    assert send_button.text() == QSerialCmd.SEND_BUTTON_TEXT


def test_command_str(q_serial_cmd):
    # Check default values
    assert q_serial_cmd._create_command_str() == "test_cmd 3 2\n\r"

    # set values for the arguments widgets
    q_serial_cmd._args[0]._spin_box.setValue(5)
    q_serial_cmd._args[1]._spin_box.setValue(3)

    assert q_serial_cmd._create_command_str() == "test_cmd 5 3\n\r"


def test_send_button_clicked(q_serial_cmd):
    # mocker.patch.object(q_serial_cmd, "_create_command_str", return_value="test_cmd 3 2\n\r")
    signal_spy = QSignalSpy(q_serial_cmd.send_clicked)

    send_button = q_serial_cmd._send_button
    QTest.mouseClick(send_button, Qt.MouseButton.LeftButton)

    assert signal_spy.count() == 1
    assert signal_spy.at(0)[0] == "test_cmd 3 2\n\r"


def test_arg_values_changed(q_serial_cmd):
    # mocker.patch.object(q_serial_cmd, "_create_command_str", return_value="test_cmd 3 2\n\r")
    signal_spy = QSignalSpy(q_serial_cmd.send_clicked)

    send_button = q_serial_cmd._send_button
    q_serial_cmd._args[0]._spin_box.setValue(5)
    q_serial_cmd._args[1]._spin_box.setValue(3)

    QTest.mouseClick(send_button, Qt.MouseButton.LeftButton)

    assert signal_spy.count() == 1
    assert signal_spy.at(0)[0] == "test_cmd 5 3\n\r"
