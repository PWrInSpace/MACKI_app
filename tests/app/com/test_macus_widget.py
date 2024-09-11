import sys
import pytest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from src.app.com.macus_widget import MacusWidget
from src.com.macus_serial import MacusSerial


@pytest.fixture
def qapp():
    app = QApplication.instance()  # Check if an instance already exists
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()


@pytest.fixture
def macus_widget() -> MacusWidget:
    macus_serial = MacusSerial()

    return MacusWidget(macus_serial)


def test_macus_widget_init(qapp, macus_widget: MacusWidget):
    assert isinstance(macus_widget._macus, MacusSerial)
    assert (
        macus_widget._macus._on_rx_callback == macus_widget._add_rx_message_to_text_box
    )
    assert (
        macus_widget._macus._on_tx_callback == macus_widget._add_tx_message_to_text_box
    )


# check _on_port_combo_clicked
def test_porto_combo_clicked(macus_widget: MacusWidget, mocker):
    available_ports = ["COM1", "COM2"]
    mocker.patch.object(
        macus_widget._macus, "get_available_ports", return_value=available_ports
    )
    QTest.mouseClick(macus_widget._port_combo, Qt.LeftButton)

    combo_items = [
        macus_widget._port_combo.itemText(i)
        for i in range(macus_widget._port_combo.count())
    ]

    assert combo_items == available_ports


# check _on_connect_button_clicked
def test_connect_button_connected(macus_widget: MacusWidget, mocker):
    # Connect
    mocker.patch.object(macus_widget._port_combo, "currentText", return_value="COM1")
    connect_mock = mocker.patch.object(macus_widget._macus, "connect")
    connected_stub = mocker.stub()
    macus_widget.connected.connect(connected_stub)

    QTest.mouseClick(macus_widget._connect_button, Qt.LeftButton)

    assert macus_widget._connect_button.text() == macus_widget.BUTTON_DISCONNECT
    connect_mock.assert_called_once_with("COM1")  # port is not set
    connected_stub.assert_called_once()


# Disconnect, right now _on_button_clicked function only check the status of serial,
# so we do not need to click the button to connect first, we only mock serial status
def test_connect_button_disconnected(macus_widget: MacusWidget, mocker):
    mocker.patch.object(macus_widget._macus, "is_connected", return_value=True)
    disconnect_mock = mocker.patch.object(macus_widget._macus, "disconnect")

    QTest.mouseClick(macus_widget._connect_button, Qt.LeftButton)

    assert macus_widget._connect_button.text() == macus_widget.BUTTON_CONNECT
    disconnect_mock.assert_called_once()


@pytest.mark.parametrize(
    "message, prefix, expected_color",
    [
        ("test\n", "", Qt.white),
        (MacusSerial.ACK + "test", "aaa", Qt.green),
        (MacusSerial.NACK + "test", "ccc", Qt.red),
        ("tdd" + MacusSerial.ACK + "a", "", Qt.white),
        ("asdasad" + MacusSerial.NACK, "", Qt.white),
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
