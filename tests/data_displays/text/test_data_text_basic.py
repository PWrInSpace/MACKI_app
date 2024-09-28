import pytest
from PySide6.QtWidgets import QHBoxLayout
from src.data_displays import DataTextBasic

NAME = "test_123"
DEFAULT_VALUE = ""


@pytest.fixture
def data_text():
    return DataTextBasic(NAME)


def test_init(data_text):
    assert data_text._name == NAME
    assert data_text._value_label.text() == DEFAULT_VALUE

    assert isinstance(data_text.layout(), QHBoxLayout)
    assert data_text.layout().itemAt(0).widget().text() == NAME.capitalize().replace(
        "_", " "
    )
    assert data_text.layout().itemAt(1).widget() == data_text._value_label


@pytest.mark.parametrize("value", [42, "Hello, World!"])
def test_update_data(data_text, value):
    data_text.update_data(value)
    assert data_text._value_label.text() == str(value)


def test_name_property(data_text):
    assert data_text.name == NAME
