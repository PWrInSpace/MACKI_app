from contextlib import nullcontext as does_not_rise

import serial
import serial.serialutil
from serial.tools.list_ports_common import ListPortInfo

import pytest
from PySide6.QtCore import QReadWriteLock, QThread
from PySide6.QtCore import Qt

from src.com.serial import SerialPort
from src.com.serial.qserial_state import QSerialStateControlThread, QSerialState
from tests.com.serial.serial_mock import SerialMock

SLEEP_TIME_MS = 20


@pytest.fixture
def pyserial_mock(mocker) -> None:
    def connect_mock(self):
        self.is_open = True

    def disconnect_mock(self):
        self.is_open = False

    mocker.patch("serial.Serial.open", connect_mock)
    mocker.patch("serial.Serial.close", disconnect_mock)

    return None


@pytest.fixture
def serial_port(pyserial_mock) -> SerialPort:
    serial = SerialPort()

    return serial


@pytest.fixture
def state_control(serial_port) -> SerialPort:
    serial = QSerialStateControlThread(serial_port)
    serial.THREAD_SLEEP_MS = 1

    return serial


def test_init_pass(serial_port):
    state_control = QSerialStateControlThread(serial_port)

    assert state_control._serial == serial_port
    assert state_control._thread_stop.occurs() is False
    assert state_control._state == QSerialState.DISCONNECTED
    assert isinstance(state_control._state_mutex, QReadWriteLock)


def test_get_state_pass(state_control, mocker):
    assert state_control.get_state() == QSerialState.DISCONNECTED

    mocker.patch.object(state_control, "_state", QSerialState.CONNECTED)
    assert state_control.get_state() == QSerialState.CONNECTED


def test_get_state_unable_to_lock(state_control, mocker):
    mocker.patch.object(
        state_control._state_mutex, "tryLockForRead", return_value=False
    )

    assert state_control.get_state() == QSerialState.UNKNOWN


def test_change_state_already_set(state_control, mocker):
    stub = mocker.stub()
    state_control.disconnected.connect(stub)

    state_control.change_state(QSerialState.DISCONNECTED)
    assert state_control._state == QSerialState.DISCONNECTED
    assert stub.call_count == 0


def test_change_state_disconnected(state_control, mocker):
    stub = mocker.stub()
    state_control.disconnected.connect(stub)

    # pathc connected state to variable
    mocker.patch.object(state_control, "_state", QSerialState.CONNECTED)

    state_control.change_state(QSerialState.DISCONNECTED)
    assert state_control._state == QSerialState.DISCONNECTED
    assert stub.call_count == 1


def test_change_state_connected(state_control, mocker):
    stub = mocker.stub()
    state_control.connected.connect(stub)

    state_control.change_state(QSerialState.CONNECTED)
    assert state_control._state == QSerialState.CONNECTED
    assert stub.call_count == 1


def test_change_state_missing(state_control, mocker):
    stub = mocker.stub()
    state_control.missed.connect(stub)

    state_control.change_state(QSerialState.MISSING)
    assert state_control._state == QSerialState.MISSING
    assert stub.call_count == 1


def test_change_state_unable_to_lock(state_control, mocker):
    stub = mocker.stub()
    state_control.missed.connect(stub)

    # patch the mutex to return False
    mocker.patch.object(
        state_control._state_mutex, "tryLockForWrite", return_value=False
    )

    state_control.change_state(QSerialState.MISSING)
    assert state_control._state == QSerialState.DISCONNECTED
    assert stub.call_count == 0


def check_connect_condition(expected, state_control, mocker):
    mocker.patch.object(state_control._serial, "is_connected", return_value=expected)

    assert state_control._check_connect_condition() is expected


def test_check_connect_condition(state_control, mocker):
    check_connect_condition(True, state_control, mocker)
    check_connect_condition(False, state_control, mocker)


def check_disonnect_disconnect(expected, state_control, mocker):
    mocker.patch.object(state_control._serial, "is_connected", return_value=expected)

    assert state_control._check_disconnect_condition() is (not expected)


def test_check_disconnect_condition(state_control, mocker):
    check_disonnect_disconnect(True, state_control, mocker)
    check_disonnect_disconnect(False, state_control, mocker)


def test_check_missing_condition_true(state_control, mocker):
    # we have to patch the pyserial port to return COM1
    available_ports = [
        ListPortInfo("COM2", True),
        ListPortInfo("COM3", True),
    ]
    mocker.patch.object(state_control._serial._serial, "_port", "COM1")
    mocker.patch.object(
        state_control._serial, "get_available_ports", return_value=available_ports
    )

    assert state_control._check_missing_condition() is True


def test_check_missing_condition_false(state_control, mocker):
    available_ports = [
        ListPortInfo("COM1", True),
        ListPortInfo("COM2", True),
    ]
    mocker.patch.object(state_control._serial._serial, "_port", "COM1")
    mocker.patch.object(
        state_control._serial, "get_available_ports", return_value=available_ports
    )

    assert state_control._check_missing_condition() is False


def test_connected_state_routine_disconnect(state_control, mocker):
    spy = mocker.spy(state_control, "change_state")

    mocker.patch.object(state_control, "_state", QSerialState.CONNECTED)
    mocker.patch.object(state_control, "_check_disconnect_condition", return_value=True)

    state_control._connected_state_routine()
    spy.assert_called_once_with(QSerialState.DISCONNECTED)


def test_connected_state_routine_missing(state_control, mocker):
    spy = mocker.spy(state_control, "change_state")

    mocker.patch.object(
        state_control, "_check_disconnect_condition", return_value=False
    )
    mocker.patch.object(state_control, "_check_missing_condition", return_value=True)

    state_control._connected_state_routine()
    spy.assert_called_once_with(QSerialState.MISSING)


def test_reconnect_to_missing_port_still_open(state_control, mocker):
    spy_change_state = mocker.spy(state_control, "change_state")
    spy_connect = mocker.spy(state_control._serial, "connect")

    mocker.patch.object(state_control._serial._serial, "_port", "COM1")

    mocker.patch.object(state_control._serial, "is_connected", return_value=True)
    mocker.patch.object(state_control._serial, "disconnect", return_value=None)
    spy_disconnect = mocker.spy(state_control._serial, "disconnect")

    state_control._reconnect_to_missing_port()
    spy_change_state.assert_called_once_with(QSerialState.CONNECTED)
    spy_connect.assert_called_once_with("COM1")
    spy_disconnect.assert_called_once()


def test_reconnect_to_missing_port_closed(state_control, mocker):
    spy_change_state = mocker.spy(state_control, "change_state")
    spy_connect = mocker.spy(state_control._serial, "connect")

    mocker.patch.object(state_control._serial._serial, "_port", "COM1")

    mocker.patch.object(state_control._serial, "is_connected", return_value=False)
    spy_disconnect = mocker.spy(state_control._serial, "disconnect")

    state_control._reconnect_to_missing_port()
    spy_change_state.assert_called_once_with(QSerialState.CONNECTED)
    spy_connect.assert_called_once_with("COM1")
    spy_disconnect.assert_not_called()


def test_missing_state_routine_still_missing(state_control, mocker):
    spy = mocker.spy(state_control, "_reconnect_to_missing_port")

    mocker.patch.object(state_control, "_check_missing_condition", return_value=True)

    state_control._missing_state_routine()
    assert state_control._reconnecting_attempts == 0
    spy.assert_not_called()


def test_missing_state_routine_reconnect(state_control, mocker):
    mocker.patch.object(state_control, "_reconnect_to_missing_port")

    mocker.patch.object(state_control, "_check_missing_condition", return_value=False)

    state_control._missing_state_routine()
    assert state_control._reconnecting_attempts == 0


def test_missing_state_routine_reconnect_raises(state_control, mocker):
    mocker.patch.object(state_control, "_check_missing_condition", return_value=False)
    mocker.patch.object(
        state_control,
        "_reconnect_to_missing_port",
        side_effect=serial.serialutil.PortNotOpenError,
    )

    with does_not_rise():
        state_control._missing_state_routine()

    assert state_control._reconnecting_attempts == 1


def test_missing_state_reconnect_exception(state_control, mocker):
    mocker.patch.object(state_control, "_check_missing_condition", return_value=False)
    mocker.patch.object(
        state_control,
        "_reconnect_to_missing_port",
        side_effect=serial.serialutil.PortNotOpenError,
    )

    with does_not_rise():
        state_control._missing_state_routine()


def test_disconnect_state_routine_connected(state_control, mocker):
    spy = mocker.spy(state_control, "change_state")

    mocker.patch.object(state_control, "_check_connect_condition", return_value=True)

    state_control._disconnected_state_routine()
    spy.assert_called_once_with(QSerialState.CONNECTED)


def test_thread_connected_state(state_control, mocker):

    mocker.patch.object(state_control, "_connected_state_routine")

    spy_connected = mocker.spy(state_control, "_connected_state_routine")
    spy_missing = mocker.spy(state_control, "_missing_state_routine")
    spy_disconnect = mocker.spy(state_control, "_disconnected_state_routine")

    state_control.change_state(QSerialState.CONNECTED)
    state_control.start()
    QThread.msleep(SLEEP_TIME_MS)

    mocker.patch.object(state_control._thread_stop, "occurs", return_value=True)
    spy_connected.assert_called()
    spy_missing.assert_not_called()
    spy_disconnect.assert_not_called()

    state_control.wait()


def test_thread_disconnected_state(state_control, mocker):
    mocker.patch.object(state_control, "_disconnected_state_routine")

    spy_connected = mocker.spy(state_control, "_connected_state_routine")
    spy_missing = mocker.spy(state_control, "_missing_state_routine")
    spy_disconnect = mocker.spy(state_control, "_disconnected_state_routine")

    state_control.start()
    QThread.msleep(SLEEP_TIME_MS)

    mocker.patch.object(state_control._thread_stop, "occurs", return_value=True)
    spy_disconnect.assert_called()
    spy_connected.assert_not_called()
    spy_missing.assert_not_called()

    state_control.wait()


def test_thread_missing_state(state_control, mocker):
    mocker.patch.object(state_control, "_missing_state_routine")

    spy_connected = mocker.spy(state_control, "_connected_state_routine")
    spy_missing = mocker.spy(state_control, "_missing_state_routine")
    spy_disconnect = mocker.spy(state_control, "_disconnected_state_routine")

    state_control.change_state(QSerialState.MISSING)
    state_control.start()
    QThread.msleep(SLEEP_TIME_MS)

    mocker.patch.object(state_control._thread_stop, "occurs", return_value=True)
    spy_missing.assert_called()
    spy_connected.assert_not_called()
    spy_disconnect.assert_not_called()

    state_control.wait()


def test_terminate(state_control):
    state_control.terminate()

    assert state_control._thread_stop.occurs() is True


def test_terminate_stop_thread(state_control):
    state_control.start()
    state_control.terminate()

    QThread.msleep(SLEEP_TIME_MS)

    assert state_control.isRunning() is False


def test_reactions_on_serial_changes(state_control, mocker):
    stub_connected = mocker.stub()
    stub_missing = mocker.stub()
    stub_disconnect = mocker.stub()

    # direct connection to avoid the event loop
    state_control.connected.connect(stub_connected, Qt.DirectConnection)
    state_control.missed.connect(stub_missing, Qt.DirectConnection)
    state_control.disconnected.connect(stub_disconnect, Qt.DirectConnection)

    serial_mock = SerialMock()
    state_control._serial = serial_mock
    state_control.start()

    serial_mock.set_open(True)

    QThread.msleep(SLEEP_TIME_MS)
    assert state_control.get_state() == QSerialState.CONNECTED
    assert stub_connected.call_count == 1
    assert stub_missing.call_count == 0
    assert stub_disconnect.call_count == 0

    # Disconnect
    serial_mock.set_open(False)

    QThread.msleep(SLEEP_TIME_MS * 2)
    assert state_control.get_state() == QSerialState.DISCONNECTED
    assert stub_connected.call_count == 1
    assert stub_missing.call_count == 0
    assert stub_disconnect.call_count == 1

    # Connect again
    serial_mock.set_open(True)

    QThread.msleep(SLEEP_TIME_MS)
    assert state_control.get_state() == QSerialState.CONNECTED
    assert stub_connected.call_count == 2
    assert stub_missing.call_count == 0
    assert stub_disconnect.call_count == 1

    # change the state to missing
    serial_mock.set_available_ports(False)

    QThread.msleep(SLEEP_TIME_MS)

    assert state_control.get_state() == QSerialState.MISSING
    assert stub_connected.call_count == 2
    assert stub_missing.call_count == 1
    assert stub_disconnect.call_count == 1

    # Close the port
    serial_mock.set_open(False)

    QThread.msleep(SLEEP_TIME_MS)
    assert state_control.get_state() == QSerialState.DISCONNECTED
    assert stub_connected.call_count == 2
    assert stub_missing.call_count == 1
    assert stub_disconnect.call_count == 2

    state_control.terminate()
    state_control.wait()
