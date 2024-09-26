# import serial as pyserial
import pytest
from contextlib import nullcontext as does_not_rise

from PySide6.QtCore import QMutex
from src.app.com.qserial import QSerial
from src.com.serial_port import SerialPort

PORT = "COM1"
DATA = b"data\r\n"


def rx_callback(data: str):
    pass


def tx_callback(data: str):
    pass


@pytest.fixture
def pyserial_mock(mocker) -> None:
    def connect_mock(self):
        self.is_open = True

    def disconnect_mock(self):
        self.is_open = False

    mocker.patch("serial.Serial.open", connect_mock)
    mocker.patch("serial.Serial.close", disconnect_mock)
    mocker.patch("serial.Serial.write")
    mocker.patch("serial.Serial.read", return_value=DATA)

    return None


@pytest.fixture
def qserial(pyserial_mock, mocker) -> SerialPort:
    serial = QSerial(PORT)
    serial.SERIAL_LOCK_TIMEOUT_MS = 1
    mocker.patch.object(serial, "is_connected", return_value=True)

    return serial


def test_init(pyserial_mock):
    serial_port = QSerial(PORT, rx_callback, tx_callback)

    assert isinstance(serial_port, SerialPort)
    # check that the arguemnts was passed correctly
    assert serial_port._serial.port is PORT
    assert serial_port._serial.baudrate == SerialPort.BAUDRATE
    assert serial_port._serial.timeout == SerialPort.READ_TIMEOUT_S
    assert serial_port._serial.write_timeout == SerialPort.WRITE_TIMEOUT_S
    assert serial_port._on_rx_callback is rx_callback
    assert serial_port._on_tx_callback is tx_callback

    # check that the QSerial attributes were initialized correctly
    assert isinstance(serial_port._serial_mutex, QMutex)


def test_write_pass(qserial):
    with does_not_rise():
        qserial.write("data")


def test_write_fail(qserial):
    qserial._serial_mutex.lock()

    with pytest.raises(TimeoutError):
        qserial.write("data")

    qserial._serial_mutex.unlock()


def test_read_pass(qserial):
    with does_not_rise():
        message = qserial.read()

    assert message == DATA.decode().strip()


def test_read_fail(qserial):
    qserial._serial_mutex.lock()

    with pytest.raises(TimeoutError):
        qserial.read()

    qserial._serial_mutex.unlock()
