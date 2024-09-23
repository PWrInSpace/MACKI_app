from src.commands.qt_args.q_arg_float import QArgFloat
import pytest
from PySide6.QtWidgets import QDoubleSpinBox
from contextlib import nullcontext as does_not_raise


ARG_NAME = "Test"
DEFAULT_VALUE = 10
MIN_VALUE = 0
MAX_VALUE = 20
UNIT = "g"
DESCRIPTION = "Description of the float argument"


@pytest.fixture
def arg_float():
    return QArgFloat(ARG_NAME, DEFAULT_VALUE, MIN_VALUE, MAX_VALUE, UNIT, DESCRIPTION)


def test_init_pass(arg_float):
    assert arg_float._name == ARG_NAME
    assert arg_float._default_value == DEFAULT_VALUE
    assert arg_float._min_value == MIN_VALUE
    assert arg_float._max_value == MAX_VALUE
    assert arg_float._unit == " " + UNIT
    assert arg_float._description == DESCRIPTION


@pytest.mark.parametrize(
    "value, raises",
    [
        ("test", pytest.raises(ValueError, match=r".*not of type.*")),
        ("10.12", pytest.raises(ValueError, match=r".*not of type.*")),
        (0, does_not_raise()),
        (0.0, does_not_raise()),
        (12e-10, does_not_raise()),
    ],
)
def test_check_type(arg_float, value, raises):
    with raises:
        arg_float._check_type(value)


def test_init_ui(arg_float):
    spin_box = arg_float._spin_box
    assert isinstance(spin_box, QDoubleSpinBox)
    assert spin_box.minimum() == MIN_VALUE
    assert spin_box.maximum() == MAX_VALUE
    assert spin_box.value() == DEFAULT_VALUE
    assert spin_box.suffix() == " " + UNIT
    assert spin_box.toolTip() == arg_float.get_full_description()
