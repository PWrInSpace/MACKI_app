import os
import pytest
import struct
from src.data_parser import DataParser

FORMAT_STRING = ">If"
DATA_NAMES = ["int", "float"]

CONFIG_FILES_DIR = os.path.dirname(os.path.abspath(__file__))


def test_init_invalid_size():
    format_string = ">If"
    data_names = ["key1", "key2", "key3"]

    with pytest.raises(ValueError):
        DataParser(format_string, data_names)


def test_init_invalid_format():
    format_string = "<ad"
    data_names = ["key1", "key2"]

    with pytest.raises(struct.error):
        DataParser(format_string, data_names)


def test_init_pass():
    data_parser = DataParser(FORMAT_STRING, DATA_NAMES)

    assert data_parser._format == FORMAT_STRING
    assert data_parser._data_keys == DATA_NAMES


def test_parse_pass():
    float_value = 3.14
    int_value = 42
    data_bytes = struct.pack(FORMAT_STRING, int_value, float_value)

    data_parser = DataParser(FORMAT_STRING, DATA_NAMES)

    parsed_data = data_parser.parse(data_bytes)

    assert len(parsed_data) == 2
    assert parsed_data[DATA_NAMES[0]] == int_value

    parsed_float = parsed_data[DATA_NAMES[1]]
    assert pytest.approx(parsed_float) == float_value


def test_parse_invalid_size():
    data_bytes = struct.pack("<I", 42)

    data_parser = DataParser(FORMAT_STRING, DATA_NAMES)

    parsed_data = data_parser.parse(data_bytes)

    assert parsed_data == {}


def test_from_json_invalid_file():
    json_file_path = os.path.join(CONFIG_FILES_DIR, "parser_config_fail.json")

    with pytest.raises(FileNotFoundError):
        DataParser.from_JSON(json_file_path)


def test_from_json_pass():
    json_file_path = os.path.join(CONFIG_FILES_DIR, "parser_config.json")

    data_parser = DataParser.from_JSON(json_file_path)

    assert data_parser._format == ">if"
    assert data_parser._data_keys == ["time", "value"]


def test_from_json_invalid_format():
    json_file_path = os.path.join(CONFIG_FILES_DIR, "invalid_parser_config.json")

    with pytest.raises(ValueError):
        DataParser.from_JSON(json_file_path)
