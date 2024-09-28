import pytest
from PySide6.QtWidgets import QWidget

from src.utils.qt.q_command_layout import QSerialCmdLay

NUMBER_OF_COLUMNS = 2


@pytest.fixture
def layout():
    return QSerialCmdLay(NUMBER_OF_COLUMNS)


def test_init_pass(layout):
    assert layout._number_of_columns == NUMBER_OF_COLUMNS
    assert layout._column_position == 0
    assert layout._args_set is False


def test_add_widget(layout):
    widget = QWidget()

    layout.addWidget(widget)
    assert layout._column_position == 1
    layout.addWidget(widget)
    assert layout._column_position == 2

    # we left one column for the send button
    with pytest.raises(ValueError):
        layout.addWidget(widget)


def test_add_widget_before_args(layout):
    widget = QWidget()

    layout.addWidgetBeforeArgs(widget)
    assert layout._column_position == 1
    layout.addWidgetBeforeArgs(widget)
    assert layout._column_position == 2
    # we left one column for the send button
    with pytest.raises(ValueError):
        layout.addWidgetBeforeArgs(widget)


def test_add_arg_widgets(layout):
    widget = QWidget()

    layout.addArgWidgets([widget])
    assert layout._column_position == 1
    assert layout._args_set is True

    with pytest.raises(ValueError):
        layout.addArgWidgets([widget, widget, widget])


def test_add_arg_widgets_position(layout):
    widget = QWidget()

    layout._number_of_columns = 10
    layout.addArgWidgets([widget, widget, widget])
    assert layout._column_position == 3


def test_add_last_widget(layout):
    widget = QWidget()

    layout.addLastWidget(widget)
    assert layout._column_position == NUMBER_OF_COLUMNS

    with pytest.raises(ValueError):
        layout.addLastWidget(widget)


def test_set_column_stretch(layout):
    for i in range(NUMBER_OF_COLUMNS):
        layout.columnStretch(i) == layout.STRETCH
