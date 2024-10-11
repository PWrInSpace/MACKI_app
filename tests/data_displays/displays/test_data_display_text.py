import pytest
from PySide6.QtWidgets import QFrame
from contextlib import nullcontext as does_not_raise

from src.data_displays import DataTextBasic, DataDisplayText, DisplayParams
from src.data_displays.displays.data_display_text import _JSONDeserializer
from src.data_displays.displays.data_display_basic import logger
from src.utils.colors import Colors

from tests.data_displays.displays.config_paths import JSON_TEXT_FILE

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
    assert layout.columnCount() == 3  # 2 values and one bar

    row = 0
    for i, data_text in enumerate(data_config):
        col = (i % COL_NUM) * 2
        assert layout.itemAtPosition(row, col).widget() == data_text

        if i % COL_NUM == COL_NUM - 1:
            row += 1
        else:
            assert (
                layout.itemAtPosition(row, col + 1).widget().frameShape()
                == QFrame.VLine
            )


def test_update_data(data_display, data_config, mocker):
    spy = mocker.spy(data_display, "update_data")
    data = {
        DATA_TEXT1: 42,
        DATA_TEXT2: "Hello, World!",
        "Not in config": "Should not be displayed",
    }

    data_display.update_data(data)

    data_text = data_display._display_configs[DATA_TEXT1]
    assert data_text._value_label.text() == str(data[DATA_TEXT1])

    data_text = data_display._display_configs[DATA_TEXT2]
    assert data_text._value_label.text() == str(data[DATA_TEXT2])

    # Check that the logger was called for the missing data
    assert spy.call_count == 1


def test_data_display_text_from_JSON(mocker):
    mocker.patch.object(_JSONDeserializer, "decode")
    spy_deserializer = mocker.spy(_JSONDeserializer, "__init__")
    spy_decoder = mocker.spy(_JSONDeserializer, "decode")

    DataDisplayText.from_JSON("test.json")

    assert spy_deserializer.call_count == 1
    assert spy_deserializer.call_args[0][1] == "test.json"
    assert spy_decoder.call_count == 1


# JSON DESERIALIZER TESTS
@pytest.fixture
def deserializer() -> _JSONDeserializer:
    return _JSONDeserializer(JSON_TEXT_FILE)


def test_from_JSON(deserializer):
    pass


@pytest.mark.parametrize(
    "cfg_dict, expected_name, expected_low, expected_up",
    [
        ({"name": "test"}, "test", float("-inf"), float("inf")),
        ({"name": "test", "lower_bound": 0}, "test", 0, float("inf")),
        ({"name": "test", "upper_bound": 100}, "test", float("-inf"), 100),
        ({"name": "test", "lower_bound": 0, "upper_bound": 100}, "test", 0, 100),
    ],
)
def test_parse_data_text_number_dict(
    deserializer, cfg_dict, expected_name, expected_low, expected_up
):
    data_text_number = deserializer._parse_data_text_number_dict(cfg_dict)

    assert data_text_number.name == expected_name
    assert data_text_number._lower_bound == expected_low
    assert data_text_number._upper_bound == expected_up


def test_parse_data_text_number_dict_error(deserializer):
    with pytest.raises(KeyError):
        deserializer._parse_data_text_number_dict({"test": "test"})


@pytest.mark.parametrize(
    "cfg_dict, expected_name, expected_values, raises",
    [
        (
            {"name": "test", "enum": {"1": "a", "2": "b"}},
            "test",
            {
                "1": DisplayParams("a", Colors.WHITE),
                "2": DisplayParams("b", Colors.WHITE),
            },
            does_not_raise(),
        ),
        (
            {
                "name": "test",
                "enum": {"1": "a", "2": "b"},
                "enum_colors": {"1": "red", "2": "mint"},
            },
            "test",
            {
                "1": DisplayParams("a", Colors.RED),
                "2": DisplayParams("b", Colors.MINT),
            },
            does_not_raise(),
        ),
        (
            {
                "name": "test",
                "enum": {"1": "a", "2": None},
                "enum_colors": {"1": "red", "2": "mint"},
            },
            "test",
            {
                "1": DisplayParams("a", Colors.RED),
                "2": DisplayParams("2", Colors.MINT),
            },
            does_not_raise(),
        ),
        (
            {"name": "test", "enum": {"1": "a", "2": "b"}, "enum_colors": {"1": "red"}},
            "test",
            {},
            pytest.raises(ValueError),
        ),
    ],
)
def test_parse_data_text_values_dict(
    deserializer, cfg_dict, expected_name, expected_values, raises
):
    with raises:
        data_text_values = deserializer._parse_data_text_values_dict(cfg_dict)

        if data_text_values:
            assert data_text_values.name == expected_name
            assert data_text_values._values._values == expected_values


def test_parse_data_text_values_dict_error(deserializer):
    with pytest.raises(KeyError):
        deserializer._parse_data_text_values_dict({"test": "test"})


def test_parse_data_text_basic_dict(deserializer):
    data_text_basic = deserializer._parse_data_text_basic_dict({"name": "test"})

    assert data_text_basic.name == "test"


def test_parse_data_text_basic_dict_error(deserializer):
    with pytest.raises(KeyError):
        deserializer._parse_data_text_basic_dict({"test": "test"})


@pytest.mark.parametrize(
    "data_list, calls_nb",
    [
        ([{"name": "test"}], 0),
        ([{"name": "test", "enum": {"1": "a", "2": "b"}}], 0),
        ([{"name": "test", "enum": {"1": "a", "2": "b"}, "lower_bound": 10}], 0),
        ([{"name": "test", "lower_bound": 10}], 1),
        ([{"name": "test", "upper_bound": -5}], 1),
        ([{"name": "test", "lower_bound": 0, "upper_bound": 100}], 1),
    ],
)
def test_data_config_from_json_dict_call_text_number(
    deserializer, data_list, calls_nb, mocker
):
    spy = mocker.spy(deserializer, "_parse_data_text_number_dict")

    json_dict = {"data": data_list}
    deserializer._data_config_from_json_dict(json_dict)

    assert spy.call_count == calls_nb


@pytest.mark.parametrize(
    "data_list, calls_nb",
    [
        ([{"name": "test", "enum": {"1": "a", "2": "b"}}], 1),
        (
            [
                {
                    "name": "test",
                    "enum": {"1": "a", "2": "b"},
                    "enum_colors": {"1": "red", "2": "mint"},
                }
            ],
            1,
        ),
        ([{"name": "test", "lower_bound": 0, "upper_bound": 100}], 0),
        ([{"name": "test"}], 0),
        ([{"name": "test", "lower_bound": 10, "enum": {"1": "a", "2": "b"}}], 1),
    ],
)
def test_data_config_from_json_dict_call_text_values(
    deserializer, data_list, calls_nb, mocker
):
    spy = mocker.spy(deserializer, "_parse_data_text_values_dict")

    json_dict = {"data": data_list}
    deserializer._data_config_from_json_dict(json_dict)

    assert spy.call_count == calls_nb


def test_json_dict_to_DataDisplayText(deserializer, mocker):
    spy = mocker.spy(deserializer, "_data_config_from_json_dict")

    json_dict = {
        "name": "test",
        "col_num": 2,
        "data": [
            {"name": "test1"},
            {"name": "test2"},
            {"name": "test3"},
        ],
    }

    data_display = deserializer._json_dict_to_DataDisplayText(json_dict)

    assert data_display.title() == "test"
    assert data_display._col_num == 2
    assert spy.call_count == 1
    assert spy.call_args[0][0] == json_dict


def test_decode(deserializer):
    data_display = deserializer.decode()

    assert data_display.title() == "Test data"
    assert data_display._col_num == 2
    assert len(data_display._display_configs) == 3
    assert list(data_display._display_configs.keys()) == [
        "title",
        "pressure",
        "valve_state",
    ]

    data_text = data_display._display_configs["title"]
    assert data_text.name == "title"

    data_text = data_display._display_configs["pressure"]
    assert data_text.name == "pressure"
    assert data_text._lower_bound == 0
    assert data_text._upper_bound == 10

    data_text = data_display._display_configs["valve_state"]
    assert data_text.name == "valve_state"
    assert data_text._values._values == {
        "1": DisplayParams("ROTATING", Colors.MINT),
        "2": DisplayParams("STATIC", Colors.GREEN),
        "3": DisplayParams("UNKNOWN", Colors.BLUE),
    }
