import pytest
from PySide6.QtWidgets import QComboBox
from PySide6.QtTest import QTest
from src.commands.qt_args.q_arg_enum import QArgEnum

ARG_NAME = "enum_arg"
ENUM_OPTIONS = {"Option 1": "option1", "Option 2": "option2", "Option 3": "option3"}
DEFAULT_NAME = "Option 2"
DESCRIPTION = "Description of the enum argument"


@pytest.fixture
def q_arg_enum():
    return QArgEnum(ARG_NAME, ENUM_OPTIONS, DEFAULT_NAME, DESCRIPTION)


def test_init_required_pass():
    # Create an instance of QArgEnum
    q_arg_enum = QArgEnum(ARG_NAME, ENUM_OPTIONS)

    # Test the initial value
    assert q_arg_enum._name == ARG_NAME
    assert q_arg_enum._enum == ENUM_OPTIONS
    assert q_arg_enum._default_name == list(ENUM_OPTIONS.keys())[0]
    assert q_arg_enum._description == ""


def test_init_full_pass(q_arg_enum):
    # Test the initial value
    assert q_arg_enum._name == ARG_NAME
    assert q_arg_enum._enum == ENUM_OPTIONS
    assert q_arg_enum._default_name == DEFAULT_NAME
    assert q_arg_enum._description == DESCRIPTION


def test_full_description(q_arg_enum):
    # Test the full description
    expected = f"{ARG_NAME.upper()}:\n{DESCRIPTION}"
    assert q_arg_enum.get_full_description() == expected


def test_init_ui(q_arg_enum):
    assert isinstance(q_arg_enum._combo_box, QComboBox)
    assert q_arg_enum._combo_box.count() == len(ENUM_OPTIONS)
    assert q_arg_enum._combo_box.currentText() == DEFAULT_NAME
    assert q_arg_enum._combo_box.toolTip() == q_arg_enum.get_full_description()


def test_get_value_str(q_arg_enum):
    assert q_arg_enum.get_value_str() == ENUM_OPTIONS[DEFAULT_NAME]


def test_choose_option(q_arg_enum):
    combo_box = q_arg_enum._combo_box
    new_option = list(ENUM_OPTIONS.keys())[2]

    assert new_option != DEFAULT_NAME, "The new option should not be the default one"
    QTest.keyClicks(combo_box, new_option)

    assert combo_box.currentText() == new_option
    assert q_arg_enum.get_value_str() == ENUM_OPTIONS[new_option]
