import pytest
from PySide6.QtWidgets import QFrame

from src.data_displays import DataTextBasic, DataDisplayText
from src.data_displays.displays.data_display_basic import logger

NAME = "test"
COL_NUM = 2
DATA_TEXT1 = "test1"
DATA_TEXT2 = "test2"
DATA_TEXT3 = "test3"


@pytest.fixture
def data_config() -> list[DataTextBasic]:
    return [
        DataTextBasic(DATA_TEXT1),
        DataTextBasic(DATA_TEXT2),
        DataTextBasic(DATA_TEXT3),
    ]


@pytest.fixture
def data_display(data_config) -> DataDisplayText:
    return DataDisplayText(data_config, NAME, COL_NUM)


def test_init_variables(data_display, data_config):
    assert data_display.title() == NAME
    assert data_display._col_num == COL_NUM
    assert data_display._display_configs == {d.name: d for d in data_config}


def test_init_layout(data_display, data_config):
    layout = data_display.layout()
    assert layout.rowCount() == 2
    assert layout.columnCount() == 3 # 2 values and one bar

    row = 0
    for i, data_text in enumerate(data_config):
        col = (i % COL_NUM) * 2
        assert layout.itemAtPosition(row, col).widget() == data_text

        if i % COL_NUM == COL_NUM - 1:
            row += 1
        else:
            assert layout.itemAtPosition(row, col + 1).widget().frameShape() == QFrame.VLine


def test_update_data(data_display, data_config, mocker):
    spy = mocker.spy(logger, "error")
    data = {
        DATA_TEXT1: 42,
        DATA_TEXT2: "Hello, World!",
        "Not in config": "Should not be displayed"
    }

    data_display.update_data(data)

    data_text = data_display._display_configs[DATA_TEXT1]
    assert data_text._value_label.text() == str(data[DATA_TEXT1])

    data_text = data_display._display_configs[DATA_TEXT2]
    assert data_text._value_label.text() == str(data[DATA_TEXT2])

    # Check that the logger was called for the missing data
    assert spy.call_count == 1
