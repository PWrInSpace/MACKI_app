import pytest

from src.commands.qt_cmd.q_command_basic import QCmdBasic

CMD_NAME = "test_cmd"
CMD_ARGS = ["arg1", "arg2"]
CMD_COLUMNS_NB = 3


class QCmdBasicTest(QCmdBasic):
    def _create_gui(self, columns_nb: int) -> None:
        self._columns_nb = columns_nb


def test_abstraction():
    with pytest.raises(NotImplementedError):
        QCmdBasic("test_cmd")


def test_init_full():
    q_command = QCmdBasicTest(CMD_NAME, CMD_ARGS, CMD_COLUMNS_NB)

    assert q_command._name == CMD_NAME
    assert q_command._args == CMD_ARGS
    assert q_command._columns_nb == CMD_COLUMNS_NB


def test_simple():
    q_command = QCmdBasicTest(CMD_NAME)

    assert q_command._name == CMD_NAME
    assert q_command._args == []
    assert q_command._columns_nb == QCmdBasicTest.DEFULT_COLUMNS_NB
