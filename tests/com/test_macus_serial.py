import serial
import pytest

from src.com.macus_serial import MacusSerial

COM_PORT = "COM1"


# tests setup
@pytest.fixture
def macus(mocker) -> MacusSerial:
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

    maucs = MacusSerial(COM_PORT)

    return maucs


def test_init_without_port(macus: MacusSerial):
    macus._serial.port = None

    assert isinstance(macus._serial, serial.Serial)
    assert macus._serial.port is None
    assert macus._serial.baudrate == MacusSerial.BAUDRATE
    assert macus._serial.timeout == MacusSerial.READ_TIMEOUT_S
    assert macus._serial.write_timeout == MacusSerial.WRITE_TIMEOUT_S


def test_init_with_port(macus: MacusSerial):
    assert isinstance(macus._serial, serial.Serial)
    assert macus._serial.port == COM_PORT
    assert macus._serial.baudrate == MacusSerial.BAUDRATE
    assert macus._serial.timeout == MacusSerial.READ_TIMEOUT_S
    assert macus._serial.write_timeout == MacusSerial.WRITE_TIMEOUT_S


def test_connect_pass(macus: MacusSerial):
    macus.connect()
    assert macus.is_connected()


def test_connect_pass_with_port(macus: MacusSerial):
    macus._serial.port = None

    macus.connect("COM3")
    assert macus._serial.port == "COM3"
    assert macus.is_connected() is True


def test_connect_pass_with_port_change(macus: MacusSerial):
    macus.connect("COM2")
    assert macus._serial.port == "COM2"
    assert macus.is_connected() is True


def test_connect_fail_port(macus: MacusSerial):
    macus._serial.port = None

    with pytest.raises(ValueError):
        macus.connect()


def test_connect_already_open(macus: MacusSerial):
    macus.connect()

    with pytest.raises(serial.SerialException):
        macus.connect()


def test_disconnect_pass(macus: MacusSerial):
    macus.connect()
    macus.disconnect()

    assert macus.is_connected() is False


def test_disconnect_fail(macus: MacusSerial):
    with pytest.raises(serial.PortNotOpenError):
        macus.disconnect()

    assert macus.is_connected() is False


def test_write_not_open(macus: MacusSerial):
    with pytest.raises(serial.PortNotOpenError):
        macus.write("test")


def test_write_pass(macus: MacusSerial, mocker):
    write_spy = mocker.spy(macus._serial, "write")

    macus.connect()
    macus.write("test")

    expected_message = "test" + MacusSerial.EOF
    write_spy.assert_called_with(expected_message.encode())
    assert write_spy.call_count == 1


def test_write_with_eof(macus: MacusSerial, mocker):
    write_spy = mocker.spy(macus._serial, "write")

    message = "test" + MacusSerial.EOF

    macus.connect()
    macus.write(message)

    write_spy.assert_called_with(message.encode())
    assert write_spy.call_count == 1


def test_read_not_open(macus: MacusSerial):
    with pytest.raises(serial.PortNotOpenError):
        macus.read()


def test_read(macus: MacusSerial, mocker):
    returned_message = b"ACK: HELLO" + MacusSerial.EOF.encode()
    mocker.patch.object(macus._serial, "read_until", return_value=returned_message)
    read_spy = mocker.spy(macus._serial, "read_until")

    macus.connect()
    message = macus.read()

    assert message == "ACK: HELLO"
    assert macus._serial.timeout == 0.1  # default timeout
    read_spy.assert_called_with(macus.EOF.encode())


# I assumed here that the serial timeout was tested by the library owner
# So I only tested the timeout change
def test_read_change_timeout(macus: MacusSerial, mocker):
    mocker.patch.object(macus._serial, "read_until", return_value=b"a")

    macus.connect()
    message = macus.read(1)

    assert message == "a"
    assert macus._serial.timeout == 1


def test_is_connected(macus: MacusSerial):
    assert macus.is_connected() is False

    macus.connect()
    assert macus.is_connected() is True

    macus.disconnect()
    assert macus.is_connected() is False


def test_write_command(macus: MacusSerial, mocker):
    # Here I mock MacusSerial.write because it is used as a last
    # element in MacusSerial.write_command, and also there is no
    # need to test the same thing twice
    write_spy = mocker.spy(macus, "write")

    macus.connect()
    macus.write_command("test")

    write_spy.assert_called_with("test")
    assert write_spy.call_count == 1


def test_write_command_with_args(macus: MacusSerial, mocker):
    # Here I mock MacusSerial.write because it is used as a last
    # element in MacusSerial.write_command, and also there is no
    # need to test the same thing twice
    write_spy = mocker.spy(macus, "write")

    macus.connect()

    command = "test"
    argumnets = ["arg1", "arg2"]

    macus.write_command(command, *argumnets)
    write_spy.assert_called_with(f"{command} {argumnets[0]} {argumnets[1]}")

    macus.write_command(command, "arg1", "arg2")
    write_spy.assert_called_with(f"{command} arg1 arg2")
