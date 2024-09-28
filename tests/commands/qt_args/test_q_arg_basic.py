import sys
import pytest
from PySide6.QtWidgets import QApplication
from src.commands.qt_args.q_arg_basic import QArgBasic

ARG_NAME = "arg"
DESCRIPTION = "Description of the basic argument"


class QArgBasicPass(QArgBasic):
    """
    Minimal required implementation to create class object.
    _init_ui in constructors throw a exception by default if
    it is not implemented.
    """

    def _init_ui(self) -> None:
        pass


#  TODO: can be moved to a conftest.py file in the future
@pytest.fixture
def qapp():
    app = QApplication.instance()  # Check if an instance already exists
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()


@pytest.fixture
def arg_basic() -> QArgBasicPass:
    return QArgBasicPass(ARG_NAME, DESCRIPTION)


def test_init_raise(qapp):
    with pytest.raises(NotImplementedError):
        QArgBasic(ARG_NAME, DESCRIPTION)


def test_init_pass(arg_basic):
    assert arg_basic._name == ARG_NAME
    assert arg_basic._description == DESCRIPTION


def test_get_value_str_error(arg_basic):
    with pytest.raises(NotImplementedError):
        arg_basic.get_value_str()


def test_get_full_description(arg_basic):
    expected = f"{ARG_NAME.upper()}:\n{DESCRIPTION}"
    assert arg_basic.get_full_description() == expected
