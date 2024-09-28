import pytest
from src.data_viewers import DataTextValues, Values
from src.utils.colors import Colors

VALUES = ["val1", "val2"]
DEFAULT_VALUE = ["def1", "def2"]
COLORS = [Colors.RED, Colors.BLUE]
NAME = "test"


@pytest.fixture
def values():
    return Values(VALUES, DEFAULT_VALUE, COLORS)


def test_init(values):
    data_text = DataTextValues(NAME, values)

    assert data_text._name == NAME
    assert data_text._values == values


def test_update_data(values):
    data_text = DataTextValues(NAME, values)

    data_text.update_data("val1")
    assert data_text._value_label.text() == "def1"
    assert data_text._value_label.styleSheet() == f"color: {Colors.RED.value}"

    data_text.update_data("val2")
    assert data_text._value_label.text() == "def2"
    assert data_text._value_label.styleSheet() == f"color: {Colors.BLUE.value}"

    data_text.update_data("not_in_values")
    assert data_text._value_label.text() == "not_in_values"
    assert data_text._value_label.styleSheet() == f"color: {Colors.RED.value}"