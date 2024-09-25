from typing import override, Callable
from PySide6.QtCore import Signal, QMutex
from src.com.serial_port import Serial, logger

from src.app.com.qserial_utils import QSerialState, SerialStateControlThread


class QSerial(Serial):
    LOCK_TIMEOUT = 1000

    connected = Signal()
    disconnected = Signal()
    missed = Signal()

    def __init__(
        self,
        com_port: str = None,
        on_rx_callback: Callable[[str], None] = None,
        on_tx_callback: Callable[[str], None] = None,
    ) -> None:
        super().__init__(com_port, on_rx_callback, on_tx_callback)
        self._state_mutex = QMutex()
        self._state = QSerialState.DISCONNECTED
        # To avoid inheriting from the QThread class, we use a thread object,
        # which controls the state of this object.
        self._state_control_thread = SerialStateControlThread(self)

    def _on_disconnected_state(self):
        """ This method is called when the widget enters the disconnected state"""
        self._state_control_loop.terminate()
        self.disconnected.emit()

    def _on_connected_state(self):
        """This method is called when the widget is enters the connected state"""
        self._state_control_thread = SerialStateControlThread(self)
        self._state_control_thread.start()
        self.connected.emit()

    def _on_missing_state(self):
        """ This method is called when the widget enters the missing state"""
        self.missed.emit()

    def _change_state(self, state: QSerialState) -> None:
        """This method changes the state

        Args:
            state (QSerialState): The new state
        """
        if not self._state_mutex.try_lock(self.LOCK_TIMEOUT):
            logger.error("Can't change the state, mutex is locked")
            return

        self._state = state
        self._state_mutex.unlock()

        logger.info(f"State changed from {self._state} to {state}")
        match state:
            case QSerialState.DISCONNECTED:
                self._on_disconnected_state()
            case QSerialState.CONNECTED:
                self._on_connected_state()
            case QSerialState.MISSING:
                self._on_missing_state()

    @override
    def connect(self, com_port: str = None) -> None:
        """ This method connects to the serial port, and changes the state to connected,
        which will start the state control loop and emit the connected signal

        Args:
            com_port (str, optional): com port to connect to. Defaults to None.
        """
        super().connect(com_port)
        self._change_state(QSerialState.CONNECTED)

    @override
    def disconnect(self) -> None:
        """This method disconnects from the serial port, and changes the state to disconnected,
        which will stop the state control loop and emit the disconnected signal
        """
        super().disconnect()
        self._change_state(QSerialState.DISCONNECTED)

    def _state_control_loop(self):
        """This method updates the status"""
        # update the port combo
        if not self._port_combo.pop_up_visible:
            self._update_availabel_ports()

        match self._state:
            case QSerialState.CONNECTED:
                self._connected_state_routine()
            case QSerialState.MISSING:
                self._missing_state_routine()

    def _connected_state_routine(self):
        """This method is called by state_control loop when serial is in the connected state"""
        ports = self._serial.get_available_ports()
        current_port = self._serial.port

        if current_port not in ports:
            self._change_state(QSerialState.MISSING)

    def _missing_state_routine(self):
        """This method is called by state_control loop when serial is in the missing state"""
        ports = self._serial.get_available_ports()
        missing_port = self._serial.port

        if missing_port in ports:
            try:
                if self._serial.is_connected():
                    self._serial.disconnect()

                self._serial.connect(missing_port)
                self._change_state(QSerialState.CONNECTED)
            except Exception as exc:
                # workaround: on error try again, sometimes the serial raises
                # an error even if the port is available, the second try should works
                logger.warning(f"Can't reconnect to the missing port: {exc}")
