import pytest
from src.data_displays import DataPlot, LivePlot
from src.data_displays.plot.data_plot import logger

X_NAME = "x_name"
Y_NAME = "y_name"


@pytest.fixture
def data_plot():
    return DataPlot(X_NAME, Y_NAME)


def test_init(mocker):
    spy = mocker.patch.object(LivePlot, "__init__")
    data_plot = DataPlot(X_NAME, Y_NAME)

    assert data_plot._x_name == X_NAME
    assert data_plot._y_name == Y_NAME

    expected_args = (X_NAME, Y_NAME, "", "lime", 200, "", "")
    spy.mock_calls[0].args[1:] == expected_args


def test_add_data_invalid_x_type(data_plot, mocker):
    spy = mocker.spy(logger, "error")
    data_plot.add_data("x", 1)

    spy.assert_called_once()


def test_add_data_invalid_y_type(data_plot, mocker):
    spy = mocker.spy(logger, "error")
    data_plot.add_data(1, "y")

    spy.assert_called_once()


def test_add_data(data_plot):
    data_plot.add_data(1, 1)

    assert data_plot.data_connector.x[-1] == 1
    assert data_plot.data_connector.y[-1] == 1


def test_x_name_property(data_plot):
    assert data_plot.x_name == X_NAME


def test_y_name_property(data_plot):
    assert data_plot.y_name == Y_NAME
