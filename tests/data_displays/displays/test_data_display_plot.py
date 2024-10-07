import pytest
from src.data_displays import DataDisplayPlot, DataPlot
from tests.data_displays.displays.config_paths import JSON_PLOT_FILE

NAME = "test"
COL_NUM = 2
X_AXIS = "time"
Y_AXIS_PLOT_1 = "pressure"
Y_AXIS_PLOT_2 = "temperature"


@pytest.fixture
def data_display():
    plots = [
        DataPlot(X_AXIS, Y_AXIS_PLOT_1),
        DataPlot(X_AXIS, Y_AXIS_PLOT_2),
    ]
    return DataDisplayPlot(plots, NAME, COL_NUM)


def test_init_varaibles(data_display):
    assert data_display.title() == NAME
    assert data_display._col_num == COL_NUM
    assert len(data_display._plots) == 2


def test_init_ui(data_display):
    assert data_display.layout().count() == 2
    assert data_display.layout().itemAt(0).widget().y_name == Y_AXIS_PLOT_1
    assert data_display.layout().itemAt(1).widget().y_name == Y_AXIS_PLOT_2


def test_update_data():
    plots = [
        DataPlot(X_AXIS, Y_AXIS_PLOT_1),
        DataPlot(X_AXIS, Y_AXIS_PLOT_2),
    ]
    data_display = DataDisplayPlot(plots, NAME, COL_NUM)

    data = {X_AXIS: 0, Y_AXIS_PLOT_1: 4, Y_AXIS_PLOT_2: 12}
    data_display.update_data(data)

    assert plots[0].data_connector.x[-1] == 0
    assert plots[0].data_connector.y[-1] == 4
    assert plots[1].data_connector.x[-1] == 0
    assert plots[1].data_connector.y[-1] == 12

    data = {X_AXIS: 1, Y_AXIS_PLOT_1: 1, "DUMMY": 1}
    data_display.update_data(data)

    assert plots[0].data_connector.x[-1] == 1
    assert plots[0].data_connector.y[-1] == 1
    assert plots[1].data_connector.x[-1] == 0
    assert plots[1].data_connector.y[-1] == 12


def test_from_JSON(mocker):
    spy = mocker.spy(DataPlot, "__init__")
    data_display = DataDisplayPlot.from_JSON(JSON_PLOT_FILE)

    assert data_display.title() == "Plots"
    assert data_display._col_num == 1
    assert len(data_display._plots) == 2

    assert data_display._plots[0].x_name == "time"
    assert data_display._plots[0].y_name == "pressure"
    expected_args = (
        "time",
        "pressure",
        "Pressure vs Time",
        "red",
        10,
        "Time (s)",
        "Pressure (Pa)",
    )  # assert spy.mock_calls[0][0] == expected_args
    assert spy.mock_calls[0].args[1:] == expected_args

    assert data_display._plots[1].x_name == "time"
    assert data_display._plots[1].y_name == "temperature"
    expected_args = ("time", "temperature", "", "lime", 200, "", "")
    assert spy.mock_calls[1].args[1:] == expected_args
