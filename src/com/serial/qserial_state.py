from enum import Enum
from typing import override
from PySide6.QtCore import QThread, QReadWriteLock, Signal
from src.utils.qt.thread_event import ThreadEvent
from src.com.serial import SerialPort, logger


class QSerialState(Enum):
    """This class represents the MacusWidget state"""

    DISCONNECTED = 0
    CONNECTED = 1
    MISSING = 2
    UNKNOWN = 99


class QSerialStateControlThread(QThread):
    """To avoid inheriting from the QThread class in QSerial, we create a
    separate thread class that controls the state of the given QSerial object.
    This task is able to automatically change the state depending on the QSerial object
    variables, such as the serial port connection status and the available ports.
    This class is also able to recconect to the missing port if it is available.

    The state is guarded by a mutex, so the state can be changed in other threads.

    Args:
        QThread: The QThread class
    """

    LOCK_TIMEOUT = 1000
    THREAD_SLEEP_MS = 50

    state_changed = Signal(QSerialState)

    def __init__(self, serial: SerialPort) -> None:
        """This method initializes the QSerialStateControlThread class

        Args:
            serial (SerialPort): The serial object
        """
        super().__init__()
        self._serial = serial  # we only use get_available_ports() and port getter
        self._thread_stop = ThreadEvent()
        self._state_mutex = QReadWriteLock()
        self._reconnecting_attempts = 0

        self._state = QSerialState.DISCONNECTED

    def get_state(self) -> QSerialState:
        """This method returns the current state

        Returns:
            QSerialState: The current state, or UNKNOWN if the mutex can't be locked
        """
        if not self._state_mutex.tryLockForRead(self.LOCK_TIMEOUT):
            logger.error("Can't get the state, mutex is locked")
            return QSerialState.UNKNOWN

        state = self._state
        self._state_mutex.unlock()

        return state

    def change_state(self, state: QSerialState):
        """This method changes the state

        Args:
            state (QSerialState): The new state
        """
        if self.get_state() == state:
            logger.warning(f"State is already set {state}")
            return

        if not self._state_mutex.tryLockForWrite(self.LOCK_TIMEOUT):
            logger.error("Can't change the state, mutex is locked")
            return

        logger.info(f"State changed from {self._state} to {state}")
        self._state = state
        self._state_mutex.unlock()

        self.state_changed.emit(self._state)

    def _check_connect_condition(self) -> bool:
        """This method checks if the serial is connected

        Returns:
            bool: True if the serial is connected, False otherwise
        """
        return self._serial.is_connected()

    def _check_disconnect_condition(self) -> bool:
        """This method checks if the serial is disconnected

        Returns:
            bool: True if the serial is disconnected, False otherwise
        """
        return not self._serial.is_connected()

    def _check_disconnect_in_missing(self) -> bool:
        """This method checks if the serial is disconnected in the missing state

        Returns:
            bool: True if the serial is disconnected in the missing state, False otherwise
        """
        return self._check_disconnect_condition() and self._reconnecting_attempts == 0

    def _check_missing_condition(self) -> bool:
        """This method checks if the serial is missing

        Returns:
            bool: True if the serial is missing, False otherwise
        """
        ports = [port.device for port in self._serial.get_available_ports()]
        return self._serial.port not in ports

    def _connected_state_routine(self):
        """This method is called by state_control loop when serial is in the connected state"""
        if self._check_disconnect_condition():
            self.change_state(QSerialState.DISCONNECTED)
        elif self._check_missing_condition():
            self.change_state(QSerialState.MISSING)

    def _reconnect_to_missing_port(self):
        """This method tries to reconnect to the missing port,
        It can raise an exception if the port is not available
        """
        missing_port = self._serial.port
        if self._serial.is_connected():
            # release the port resources before reconnecting
            self._serial.disconnect()

        self._serial.connect(missing_port)
        self.change_state(QSerialState.CONNECTED)

    def _missing_state_routine(self):
        """This method is called by state_control loop when serial is in the missing state"""
        if not self._check_missing_condition():
            try:
                self._reconnecting_attempts += 1  # TODO: add a limit for the attempts
                self._reconnect_to_missing_port()
            except Exception as exc:
                # workaround: on error try again, sometimes the serial raises
                # an error even if the port is available, the second try should works
                logger.warning(f"Can't reconnect to the missing port: {exc}")
            else:
                self._reconnecting_attempts = 0

        elif self._check_disconnect_in_missing():
            self.change_state(QSerialState.DISCONNECTED)

    def _disconnected_state_routine(self):
        """This method is called by state_control loop when serial is in the disconnected state"""
        if self._check_connect_condition():
            self.change_state(QSerialState.CONNECTED)

    def run(self) -> None:
        """This method runs the thread"""
        while not self._thread_stop.occurs():
            # this gives immidiately check for the stop signal, after handling the state
            QThread.msleep(self.THREAD_SLEEP_MS)

            match self._state:
                case QSerialState.CONNECTED:
                    self._connected_state_routine()
                case QSerialState.MISSING:
                    self._missing_state_routine()
                case QSerialState.DISCONNECTED:
                    self._disconnected_state_routine()

    @override
    def terminate(self) -> None:
        """This method terminates the thread"""
        self._thread_stop.set()
