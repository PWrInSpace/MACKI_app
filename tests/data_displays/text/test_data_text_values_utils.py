import pytest
from src.data_displays import Values, DisplayParams
from src.utils.colors import Colors

VALUES = ["val1", "val2"]
DEFAULT_VALUE = ["def1", "def2"]
COLORS = [Colors.RED, Colors.BLUE]


@pytest.fixture
def values() -> Values:
    return Values(VALUES, DEFAULT_VALUE, COLORS)


def test_init_pass(values):
    assert values._values.keys() == set(VALUES)
    expected_params = [
        DisplayParams(value, color) for value, color in zip(DEFAULT_VALUE, COLORS)
    ]
    for expected, param in zip(expected_params, values._values.values()):
        assert expected.display_value == param.display_value
        assert expected.color == param.color


def test_init_fail():
    with pytest.raises(ValueError):
        Values(VALUES, DEFAULT_VALUE, COLORS[:-1])


def test_init_replace_none():
    values = Values(VALUES, [None, None], COLORS)

    expected_params = [
        DisplayParams(value, color) for value, color in zip(VALUES, COLORS)
    ]
    for expected, param in zip(expected_params, values._values.values()):
        assert expected.display_value == param.display_value
        assert expected.color == param.color


def test_contains(values):
    for value in VALUES:
        assert value in values

    assert "not_in_values" not in values


def test_getitem(values):
    for value, expected in zip(VALUES, DEFAULT_VALUE):
        assert values[value].display_value == expected
        assert values[value].color == COLORS[DEFAULT_VALUE.index(expected)]

    assert values["not_in_values"] is None


def test_getitem_replace_none():
    values = Values(VALUES, [None, None], COLORS)

    for value, expected in zip(VALUES, VALUES):
        assert values[value].display_value == expected
        assert values[value].color == COLORS[VALUES.index(expected)]


def test_add_value(values):
    new_value = "new_val"
    new_display_value = "new_display_val"
    new_color = Colors.GREEN

    values.add_value(new_value, new_display_value, new_color)

    assert new_value in values
    assert values[new_value].display_value == new_display_value
    assert values[new_value].color == new_color


def test_add_value_display_none(values):
    new_value = "new_val"
    new_display_value = None
    new_color = Colors.GREEN

    values.add_value(new_value, new_display_value, new_color)

    assert new_value in values
    assert values[new_value].display_value == new_value
    assert values[new_value].color == new_color


def test_add_value_duplicate(values):
    new_value = VALUES[0]
    new_display_value = "new_display_val"
    new_color = Colors.GREEN

    with pytest.raises(ValueError):
        values.add_value(new_value, new_display_value, new_color)
