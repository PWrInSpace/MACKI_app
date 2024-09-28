import pytest

from serial.tools.list_ports_common import ListPortInfo

from PySide6.QtCore import Qt, QThread
from PySide6.QtTest import QTest

from src.app.com.macus_widget import MacusWidget
from src.com.serial import QSerial, QSerialState, QSerialStateControlThread
from src.utils.colors import Colors


@pytest.fixture
def macus_widget(mocker):
    widget = MacusWidget()
    yield widget

    # patch disconnect to avoid exception
    mocker.patch.object(widget._com_serial, "disconnect")
    widget.quit()


def test_macus_widget_init(macus_widget: MacusWidget):
    assert isinstance(macus_widget._com_serial, QSerial)
    assert macus_widget._com_serial_state.isRunning() is True
    assert (
        macus_widget._com_serial._on_rx_callback
        == macus_widget._add_rx_message_to_text_box
    )
    assert (
        macus_widget._com_serial._on_tx_callback
        == macus_widget._add_tx_message_to_text_box
    )


# check _on_port_combo_clicked
def test_porto_combo_clicked(macus_widget: MacusWidget, mocker):
    available_ports = [
        ListPortInfo("COM1", True),
        ListPortInfo("COM2", True),
    ]
    mocker.patch.object(
        macus_widget._com_serial, "get_available_ports", return_value=available_ports
    )
    QTest.mouseClick(macus_widget._port_combo, Qt.LeftButton)

    combo_items = [
        macus_widget._port_combo.itemText(i)
        for i in range(macus_widget._port_combo.count())
    ]

    assert combo_items == [port.name for port in available_ports]


# check _on_connect_button_clicked
def test_connect_button_connected(macus_widget: MacusWidget, mocker):
    # Do not check state, because it was tested in test_qserial_state.py
    mocker.patch.object(macus_widget._port_combo, "currentText", return_value="COM1")
    connect_mock = mocker.patch.object(macus_widget._com_serial, "connect")

    QTest.mouseClick(macus_widget._connect_button, Qt.LeftButton)

    QThread.msleep(QSerialStateControlThread.THREAD_SLEEP_MS * 2)

    assert macus_widget._connect_button.text() == macus_widget.BUTTON_DISCONNECT
    connect_mock.assert_called_once_with("COM1")  # port is not set


# Disconnect, right now _on_button_clicked function only check the status of serial,
# so we do not need to click the button to connect first, we only mock serial status
def test_connect_button_disconnected(macus_widget: MacusWidget, mocker):
    mocker.patch.object(macus_widget._com_serial, "is_connected", return_value=True)
    disconnect_mock = mocker.patch.object(macus_widget._com_serial, "disconnect")

    QTest.mouseClick(macus_widget._connect_button, Qt.LeftButton)

    assert macus_widget._connect_button.text() == macus_widget.BUTTON_CONNECT
    disconnect_mock.assert_called_once()


@pytest.mark.parametrize(
    "state, color",
    [
        (QSerialState.DISCONNECTED, Colors.RED),
        (QSerialState.CONNECTED, Colors.GREEN),
        (QSerialState.MISSING, Colors.YELLOW),
        (QSerialState.UNKNOWN, Colors.WHITE),
    ],
)
def test_update_state_label(macus_widget: MacusWidget, state, color):
    macus_widget._update_state_label(state)

    assert macus_widget._state_label.text() == state.name
    assert macus_widget._state_label.styleSheet() == f"color: {color.value};"


@pytest.mark.parametrize(
    "message, prefix, expected_color",
    [
        ("test\n", "", Qt.white),
        (QSerial.ACK + "test", "aaa", Qt.green),
        (QSerial.NACK + "test", "ccc", Qt.red),
        ("tdd" + QSerial.ACK + "a", "", Qt.white),
        ("asdasad" + QSerial.NACK, "", Qt.white),
    ],
)
def test_add_message_to_text_box(
    message, prefix, expected_color, macus_widget: MacusWidget
):
    macus_widget._add_message_to_text_box(message, prefix)

    if not message.endswith("\n"):
        message += "\n"

    message = prefix + message
    assert macus_widget._text_edit.toPlainText() == message
    assert macus_widget._text_edit.textColor() == expected_color


def test_add_tx_message_to_text_box(macus_widget: MacusWidget):
    macus_widget._add_tx_message_to_text_box("test")

    expected_message = macus_widget.TX_PREFIX + "test\n"
    assert macus_widget._text_edit.toPlainText() == expected_message
    assert macus_widget._text_edit.textColor() == Qt.white


def test_add_rx_message_to_text_box(macus_widget: MacusWidget):
    macus_widget._add_rx_message_to_text_box("test")

    expected_message = macus_widget.RX_PREFIX + "test\n"
    assert macus_widget._text_edit.toPlainText() == expected_message
    assert macus_widget._text_edit.textColor() == Qt.white


def test_timer_routine_popup_not_visible(macus_widget, mocker):
    spy = mocker.spy(macus_widget, "_update_availabel_ports")
    mocker.patch.object(
        macus_widget._port_combo, "is_pop_up_visible", return_value=False
    )

    macus_widget._timer_routine()

    spy.assert_called_once()


def test_timer_routine_popup_visible(macus_widget, mocker):
    spy = mocker.spy(macus_widget, "_update_availabel_ports")
    mocker.patch.object(
        macus_widget._port_combo, "is_pop_up_visible", return_value=True
    )

    macus_widget._timer_routine()

    spy.assert_not_called()


def test_com_serial_property(macus_widget):
    assert macus_widget.com_serial == macus_widget._com_serial


def test_com_state_changed_property(macus_widget):
    assert (
        macus_widget.com_state_changed == macus_widget._com_serial_state.state_changed
    )
