import pytest
from PySide6.QtWidgets import QSpinBox
from src.commands.qt_args.q_arg_value import QArgValue
from contextlib import nullcontext as does_not_raise

ARG_NAME = "Test"
DEFAULT_VALUE = 10
MIN_VALUE = 0
MAX_VALUE = 20
UNIT = "g"
DESCRIPTION = "Description of the value argument"


class QArgValueTest(QArgValue):
    def _check_type(self, value: int | float) -> None:
        if not isinstance(value, (int, float, type(None))):
            raise ValueError(f"Invalid value type: {type(value)}")

    def _create_spin_box(self) -> QSpinBox:
        return QSpinBox()


@pytest.fixture
def arg_value():
    return QArgValueTest(
        ARG_NAME, DEFAULT_VALUE, MIN_VALUE, MAX_VALUE, UNIT, DESCRIPTION
    )


def test_init_fail():
    with pytest.raises(NotImplementedError):
        QArgValue(ARG_NAME, DEFAULT_VALUE, MIN_VALUE, MAX_VALUE, UNIT, DESCRIPTION)


@pytest.mark.parametrize(
    "default_value, raises",
    [
        ("test", pytest.raises(ValueError)),
        (20.0, does_not_raise()),
        (12, does_not_raise()),
    ],
)
def test_init_default_value_type(default_value, raises):
    with raises:
        QArgValueTest(ARG_NAME, default_value)


@pytest.mark.parametrize(
    "min_value, raises",
    [
        ("test", pytest.raises(ValueError)),
        (1.0, does_not_raise()),
        (3, does_not_raise()),
    ],
)
def test_init_min_value_type(min_value, raises):
    with raises:
        QArgValueTest(ARG_NAME, DEFAULT_VALUE, min_value)


@pytest.mark.parametrize(
    "max_value, raises",
    [
        ("test", pytest.raises(ValueError)),
        (22.0, does_not_raise()),
        (32, does_not_raise()),
    ],
)
def test_init_max_value_type(max_value, raises):
    with raises:
        QArgValueTest(ARG_NAME, DEFAULT_VALUE, MIN_VALUE, max_value)


@pytest.mark.parametrize(
    "default_value, min_value, max_value, raises",
    [
        (0, 20, 0, pytest.raises(ValueError, match=r"Min value must be less than*")),
        (0, 0, 0, does_not_raise()),
        (0, 0, 20, does_not_raise()),
        (
            -5,
            0,
            20,
            pytest.raises(ValueError, match=r"Default value must be greater than*"),
        ),
        (
            25,
            0,
            20,
            pytest.raises(ValueError, match=r"Default value must be less than*"),
        ),
        (20, 0, 20, does_not_raise()),
    ],
)
def test_init_invalid_values(default_value, min_value, max_value, raises):
    with raises:
        QArgValueTest(ARG_NAME, default_value, min_value, max_value)


def test_init_no_min_value():
    arg_value = QArgValueTest(ARG_NAME, DEFAULT_VALUE, None, MAX_VALUE)
    assert arg_value._min_value is None


def test_init_no_max_value():
    arg_value = QArgValueTest(ARG_NAME, DEFAULT_VALUE, MIN_VALUE, None)
    assert arg_value._max_value is None


def test_init_no_unit():
    arg_value = QArgValueTest(ARG_NAME, DEFAULT_VALUE, MIN_VALUE, MAX_VALUE)
    assert arg_value._unit == ""


def test_init_no_description():
    arg_value = QArgValueTest(ARG_NAME, DEFAULT_VALUE, MIN_VALUE, MAX_VALUE)
    assert arg_value._description == ""


def test_init_pass(arg_value):
    assert arg_value._default_value == DEFAULT_VALUE
    assert arg_value._min_value == MIN_VALUE
    assert arg_value._max_value == MAX_VALUE
    assert arg_value._unit == f" {UNIT}" if UNIT else ""
    assert arg_value._description == DESCRIPTION


def test_init_ui(arg_value):
    spin_box = arg_value._spin_box
    assert isinstance(spin_box, QSpinBox)
    assert spin_box.minimum() == MIN_VALUE
    assert spin_box.maximum() == MAX_VALUE
    assert spin_box.value() == DEFAULT_VALUE
    assert spin_box.suffix() == " " + UNIT
    assert spin_box.toolTip() == arg_value.get_full_description()


@pytest.mark.parametrize(
    "value, expected",
    [
        (MIN_VALUE, True),
        (MAX_VALUE, True),
        (MAX_VALUE - 1, True),
        (MAX_VALUE + 1, False),
        (MIN_VALUE - 1, False),
    ],
)
def test_check_value(arg_value, value, expected):
    assert arg_value.check_value(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (MIN_VALUE, str(MIN_VALUE)),
        (MAX_VALUE, str(MAX_VALUE)),
        (MAX_VALUE - 1, str(MAX_VALUE - 1)),
        # Should not raise ValueError due to the limits on SpinBox
        (MAX_VALUE + 1, str(MAX_VALUE)),
        (MIN_VALUE - 1, str(MIN_VALUE)),
    ],
)
def test_get_value_str(arg_value, value, expected):
    spin_box = arg_value._spin_box
    spin_box.setValue(value)

    value = arg_value.get_value_str()

    assert value == expected


def test_get_full_description(arg_value):
    description = arg_value.get_full_description()

    assert DESCRIPTION in description
    assert f"Min: {MIN_VALUE}" in description
    assert f"Max: {MAX_VALUE}" in description


def test_get_full_description_no_min_max(arg_value):
    arg_value._min_value = None
    arg_value._max_value = None

    description = arg_value.get_full_description()

    assert DESCRIPTION in description
    assert "Min" not in description
    assert "Max" not in description
