import pytest
from src.data_displays import DataTextNumber
from src.utils.colors import Colors

NAME = "test_123"
DEFAULT_VALUE = ""
LOWER_BOUND = -10
UPPER_BOUND = 10


@pytest.fixture
def data_text():
    return DataTextNumber(NAME, LOWER_BOUND, UPPER_BOUND)


def test_init_default():
    data_text = DataTextNumber(NAME)
    assert data_text._name == NAME

    assert data_text._lower_bound == float("-inf")
    assert data_text._upper_bound == float("inf")


def test_invalid_lower_bound_type():
    with pytest.raises(TypeError):
        DataTextNumber(NAME, lower_bound="invalid")


def test_invalid_upper_bound_type():
    with pytest.raises(TypeError):
        DataTextNumber(NAME, upper_bound="invalid")


def test_init_lower_bound():
    lower_bound = 0
    data_text = DataTextNumber(NAME, lower_bound=lower_bound)
    assert data_text._name == NAME

    assert data_text._lower_bound == lower_bound
    assert data_text._upper_bound == float("inf")


def test_init_upper_bound():
    upper_bound = 100
    data_text = DataTextNumber(NAME, upper_bound=upper_bound)
    assert data_text._name == NAME

    assert data_text._lower_bound == float("-inf")
    assert data_text._upper_bound == upper_bound


def test_both_bounds(data_text):
    assert data_text._name == NAME

    assert data_text._lower_bound == LOWER_BOUND
    assert data_text._upper_bound == UPPER_BOUND


def test_init_bounds_error():
    lower_bound = 100
    upper_bound = 0
    with pytest.raises(ValueError):
        DataTextNumber(NAME, lower_bound=lower_bound, upper_bound=upper_bound)


@pytest.mark.parametrize(
    "value, expected_color",
    [
        (0, Colors.WHITE),
        (LOWER_BOUND, Colors.WHITE),
        (UPPER_BOUND, Colors.WHITE),
        (LOWER_BOUND - 1, Colors.RED),
        (UPPER_BOUND + 1, Colors.RED),
    ],
)
def test_update_data(data_text, value, expected_color):
    data_text.update_data(value)
    assert data_text._value_label.text() == str(value)
    assert data_text._value_label.styleSheet() == f"color: {expected_color.value}"


@pytest.mark.parametrize(
    "value, expected_color",
    [
        (0, Colors.WHITE),
        (LOWER_BOUND, Colors.WHITE),
        (UPPER_BOUND, Colors.WHITE),
        (LOWER_BOUND - 1, Colors.WHITE),
        (UPPER_BOUND + 1, Colors.WHITE),
        (1_000_000_000, Colors.WHITE),
        (-1_000_000_000, Colors.WHITE),
    ],
)
def test_update_data_default_bounds(value, expected_color):
    data_text = DataTextNumber(NAME)
    data_text.update_data(value)
    assert data_text._value_label.text() == str(value)
    assert data_text._value_label.styleSheet() == f"color: {expected_color.value}"


def test_check_value_label_text_format(data_text):
    data_text.update_data(1.2345)
    assert data_text._value_label.text() == "1.23"

    data_text.update_data(1)
    assert data_text._value_label.text() == "1"

    data_text.update_data(1.0)
    assert data_text._value_label.text() == "1.00"
