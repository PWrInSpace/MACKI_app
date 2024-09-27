from typing import override, Callable
from PySide6.QtCore import QMutex
from src.com.serial import SerialPort


class QSerial(SerialPort):
    SERIAL_LOCK_TIMEOUT_MS = 1000

    def __init__(
        self,
        com_port: str = None,
        baudrate: int = 115200,
        on_rx_callback: Callable[[str], None] = None,
        on_tx_callback: Callable[[str], None] = None,
    ) -> None:
        """This method initializes the MacusSerial class

        Args:
            com_port (str, optional): com port to connect to. Defaults to None.
            on_rx_callback (Callable[[str], None], optional): callback for received data.
            Defaults to None.
            on_tx_callback (Callable[[str], None], optional): callback for transmitted data.
            Defaults to None
        """
        super().__init__(com_port, baudrate,  on_rx_callback, on_tx_callback)
        self._serial_mutex = QMutex()

    @override
    def write(self, data: str) -> None:
        """ This method writes to the serial port.

        .. note::
            The method is thread-safe.

        Args:
            data (str): The data to write

        Raises:
            TimeoutError: Can't write to a serial: unable to lock the mutex
        """
        if not self._serial_mutex.tryLock(self.SERIAL_LOCK_TIMEOUT_MS):
            raise TimeoutError("Can't write to a serial: unable to lock the mutex")

        try:
            super().write(data)
        finally:
            self._serial_mutex.unlock()

    @override
    def read(self, read_timeout_s: float = 0.1) -> str:
        """ This method reads from the serial port.

        .. note::
            The method is thread-safe.

        Args:
            read_timeout_s (float, optional): _description_. Defaults to 0.1.

        Raises:
            TimeoutError: _description_

        Returns:
            str: _description_
        """
        if not self._serial_mutex.tryLock(self.SERIAL_LOCK_TIMEOUT_MS):
            raise TimeoutError("Can't read from serial: unable to lock the mutex")

        try:
            message = super().read(read_timeout_s)
        finally:
            self._serial_mutex.unlock()

        return message
