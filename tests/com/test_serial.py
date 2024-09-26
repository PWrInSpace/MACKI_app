import serial as pyserial
import pytest
from contextlib import nullcontext as does_not_rise

from src.com.serial_port import SerialPort

COM_PORT = "COM1"


# tests setup
@pytest.fixture
def pyserial_mock(mocker) -> SerialPort:
    def connect_mock(self):
        self.is_open = True

    def disconnect_mock(self):
        self.is_open = False

    def timeout_setter_mock(self, timeout):
        self._timeout = timeout

    mocker.patch("serial.Serial.open", connect_mock)
    mocker.patch("serial.Serial.close", disconnect_mock)
    mocker.patch("serial.Serial.timeout", timeout_setter_mock)
    mocker.patch("serial.Serial.write")

    return None


@pytest.fixture
def serial_port(pyserial_mock) -> SerialPort:
    serial_port = SerialPort(COM_PORT)

    return serial_port


def test_init_without_port(pyserial_mock):
    serial_port = SerialPort()

    assert isinstance(serial_port._serial, pyserial.Serial)
    assert serial_port._serial.port is None
    assert serial_port._serial.baudrate == SerialPort.BAUDRATE
    assert serial_port._serial.timeout == SerialPort.READ_TIMEOUT_S
    assert serial_port._serial.write_timeout == SerialPort.WRITE_TIMEOUT_S
    assert serial_port._on_rx_callback is None
    assert serial_port._on_tx_callback is None


def test_init_with_port(serial_port: SerialPort):
    assert isinstance(serial_port._serial, pyserial.Serial)
    assert serial_port._serial.port == COM_PORT
    assert serial_port._serial.baudrate == SerialPort.BAUDRATE
    assert serial_port._serial.timeout == SerialPort.READ_TIMEOUT_S
    assert serial_port._serial.write_timeout == SerialPort.WRITE_TIMEOUT_S
    assert serial_port._on_rx_callback is None
    assert serial_port._on_tx_callback is None


def test_init_with_port_and_callbacks(pyserial_mock):
    def callback(data: str):
        pass

    serial_port = SerialPort(COM_PORT, callback, callback)

    assert isinstance(serial_port._serial, pyserial.Serial)
    assert serial_port._serial.port == COM_PORT
    assert serial_port._serial.baudrate == SerialPort.BAUDRATE
    assert serial_port._serial.timeout == SerialPort.READ_TIMEOUT_S
    assert serial_port._serial.write_timeout == SerialPort.WRITE_TIMEOUT_S
    assert serial_port._on_rx_callback == callback
    assert serial_port._on_tx_callback == callback


def test_connect_pass(serial_port: SerialPort):
    serial_port.connect()
    assert serial_port.is_connected()


def test_connect_pass_with_port(serial_port: SerialPort):
    serial_port._serial.port = None

    serial_port.connect("COM3")
    assert serial_port._serial.port == "COM3"
    assert serial_port.is_connected() is True


def test_connect_pass_with_port_change(serial_port: SerialPort):
    serial_port.connect("COM2")
    assert serial_port._serial.port == "COM2"
    assert serial_port.is_connected() is True


def test_connect_fail_port(serial_port: SerialPort):
    serial_port._serial.port = None

    with pytest.raises(ValueError):
        serial_port.connect()


def test_connect_already_open(serial_port: SerialPort):
    serial_port.connect()

    with pytest.raises(pyserial.SerialException):
        serial_port.connect()


def test_disconnect_pass(serial_port: SerialPort):
    serial_port.connect()
    serial_port.disconnect()

    assert serial_port.is_connected() is False


def test_disconnect_fail(serial_port: SerialPort):
    with pytest.raises(pyserial.PortNotOpenError):
        serial_port.disconnect()

    assert serial_port.is_connected() is False


def test_write_not_open(serial_port: SerialPort):
    with pytest.raises(pyserial.PortNotOpenError):
        serial_port.write("test")


def test_write_pass(serial_port: SerialPort, mocker):
    write_spy = mocker.spy(serial_port._serial, "write")

    serial_port.connect()
    serial_port.write("test")

    expected_message = "test" + SerialPort.EOF
    write_spy.assert_called_with(expected_message.encode())
    assert write_spy.call_count == 1


def test_write_with_eof(serial_port: SerialPort, mocker):
    write_spy = mocker.spy(serial_port._serial, "write")

    message = "test" + SerialPort.EOF

    serial_port.connect()
    serial_port.write(message)

    write_spy.assert_called_with(message.encode())
    assert write_spy.call_count == 1


def test_read_not_open(serial_port: SerialPort):
    with pytest.raises(pyserial.PortNotOpenError):
        serial_port.read()


def test_read(serial_port: SerialPort, mocker):
    returned_message = b"ACK: HELLO" + SerialPort.EOF.encode()
    mocker.patch.object(serial_port._serial, "read_until", return_value=returned_message)
    read_spy = mocker.spy(serial_port._serial, "read_until")

    serial_port.connect()
    message = serial_port.read()

    assert message == "ACK: HELLO"
    assert serial_port._serial.timeout == 0.1  # default timeout
    read_spy.assert_called_with(serial_port.EOF.encode())


# I assumed here that the serial_port timeout was tested by the library owner
# So I only tested the timeout change
def test_read_change_timeout(serial_port: SerialPort, mocker):
    mocker.patch.object(serial_port._serial, "read_until", return_value=b"a")

    serial_port.connect()
    message = serial_port.read(1)

    assert message == "a"
    assert serial_port._serial.timeout == 1


def test_is_connected(serial_port: SerialPort):
    assert serial_port.is_connected() is False

    serial_port.connect()
    assert serial_port.is_connected() is True

    serial_port.disconnect()
    assert serial_port.is_connected() is False


def test_get_available_ports_call(serial_port):
    with does_not_rise():
        serial_port.get_available_ports()


def test_get_available_ports_ret_value(serial_port, mocker):
    mocker.patch("serial.tools.list_ports.comports", return_value=[COM_PORT])

    ports = serial_port.get_available_ports()
    assert ports == [COM_PORT]


def test_set_rx_callback(serial_port: SerialPort):
    def callback(data: str):
        pass

    serial_port.set_rx_callback(callback)

    assert serial_port._on_rx_callback == callback


def test_set_tx_callback(serial_port: SerialPort):
    def callback(data: str):
        pass

    serial_port.set_tx_callback(callback)

    assert serial_port._on_tx_callback == callback


def test_write_with_callback(serial_port: SerialPort, mocker):
    stub = mocker.stub()

    serial_port.set_tx_callback(stub)

    serial_port.connect()
    serial_port.write("test")

    stub.assert_called_with("test")


def test_read_with_callback(serial_port: SerialPort, mocker):
    mocker.patch.object(serial_port._serial, "read_until", return_value=b"a\n\r")
    stub = mocker.stub()

    serial_port.set_rx_callback(stub)

    serial_port.connect()
    serial_port.read()

    stub.assert_called_with("a")


def test_write_command(serial_port: SerialPort, mocker):
    # Here I mock SerialPort):.write because it is used as a last
    # element in SerialPort):.write_command, and also there is no
    # need to test the same thing twice
    write_spy = mocker.spy(serial_port, "write")

    serial_port.connect()
    serial_port.write_command("test")

    write_spy.assert_called_with("test")
    assert write_spy.call_count == 1


def test_write_command_with_args(serial_port: SerialPort, mocker):
    # Here I mock SerialPort):.write because it is used as a last
    # element in SerialPort):.write_command, and also there is no
    # need to test the same thing twice
    write_spy = mocker.spy(serial_port, "write")

    serial_port.connect()

    command = "test"
    argumnets = ["arg1", "arg2"]

    serial_port.write_command(command, *argumnets)
    write_spy.assert_called_with(f"{command} {argumnets[0]} {argumnets[1]}")

    serial_port.write_command(command, "arg1", "arg2")
    write_spy.assert_called_with(f"{command} arg1 arg2")


def test_port_property(serial_port: SerialPort):
    assert serial_port.port == COM_PORT