import logging
from typing import override, Callable
import serial
import serial.tools.list_ports

from serial.serialutil import PortNotOpenError, SerialException

from src.com.abstract.com_proto_basic import ComProtoBasic

logger = logging.getLogger(__name__)


class SerialPort(ComProtoBasic):
    EOF = "\r\n"
    READ_TIMEOUT_S = 0.1
    WRITE_TIMEOUT_S = 0.1

    ACK = "OK: "
    NACK = "ERR: "

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
        self._serial = serial.Serial()
        self._serial.port = com_port
        self._serial.baudrate = baudrate
        self._serial.timeout = self.READ_TIMEOUT_S
        self._serial.write_timeout = self.WRITE_TIMEOUT_S

        self._on_rx_callback = on_rx_callback
        self._on_tx_callback = on_tx_callback

        self._ack_bytes = self.ACK.encode()
        self._nack_bytes = self.NACK.encode()

    @override
    def connect(self, com_port: str = None) -> None:
        """This method connects to the serial port

        Args:
            com_port (str, optional): com port to connect to. Defaults to None.

        Raises:
            SerialException: Serial port is already open
            ValueError: COM port not provided
        """
        if self._serial.is_open:
            raise SerialException("Serial port is already open")

        self._serial.port = com_port or self._serial.port
        if not self._serial.port:
            raise ValueError("COM port not provided")

        self._serial.open()

    @override
    def disconnect(self) -> None:
        """This method disconnects from the serial port

        Raises:
            PortNotOpenError: Serial port is not open
        """
        if not self._serial.is_open:
            raise PortNotOpenError()

        self._serial.close()

    @override
    def write(self, data: str) -> None:
        """This method writes data to the serial port

        Args:
            data (str): The data to write

        Raises:
            PortNotOpenError: Serial port is not open
        """
        if not self.is_connected():
            raise PortNotOpenError()

        tx_data = data
        if not data.endswith(self.EOF):
            tx_data += self.EOF

        self._serial.reset_input_buffer()
        self._serial.write(tx_data.encode())

        if self._on_tx_callback:
            self._on_tx_callback(data)

    @override
    def read(self, read_timeout_s: float = 0.1) -> str:
        """This method reads data from the serial port

        Args:
            read_timeout_s (float, optional): read timeout. Defaults to 0.1.

        Raises:
            PortNotOpenError: Serial port is not open

        Returns:
            str: The data read from the serial port
        """
        if not self.is_connected():
            raise PortNotOpenError()

        self._serial.timeout = read_timeout_s
        raw_response = self._serial.read_until(self.EOF.encode())
        response = raw_response.decode().strip()

        if self._on_rx_callback:
            self._on_rx_callback(response)

        return response

    def read_raw_until_response(self, read_timeout_s: float = 0.1) -> bytes:
        iterations = 0
        while iterations < 10:
            iterations += 1
            line = self._serial.read_until(self.EOF.encode())

            if self._ack_bytes in line or self._nack_bytes in line:
                return line

        return b""

    @override
    def is_connected(self) -> bool:
        """This method checks if the device is connected

        Returns:
            bool: True if the device is connected, False otherwise
        """
        return self._serial.is_open

    @staticmethod
    def get_available_ports() -> list[str]:
        """This method lists the available COM ports

        Returns:
            list[str]: The list of available COM ports
        """
        return serial.tools.list_ports.comports()

    def set_rx_callback(self, callback: Callable[[str], None]) -> None:
        """This method sets the callback for received data

        Args:
            callback (Callable[[str], None]): The callback function
        """
        self._on_rx_callback = callback

    def set_tx_callback(self, callback: Callable[[str], None]) -> None:
        """This method sets the callback for transmitted data

        Args:
            callback (Callable[[str], None]): The callback function
        """
        self._on_tx_callback = callback

    def read_until_response(self) -> str:
        """This method reads the response from the device

        Returns:
            str: The response from the device
        """
        response = self.read_raw_until_response()

        if not response:
            return None

        decoded_response = response.decode().strip()
        self._on_rx_callback(decoded_response)

        return decoded_response


    def write_command(self, command_name: str, *argv) -> str:
        """This method writes a command to the serial port and reads the response

        Args:
            command_name (str): The command to write

        Returns:
            str: The response from the device
        """
        command = command_name

        for arg in argv:
            command += f" {arg}"

        self.write(command)

    @property
    def port(self) -> str:
        """This method returns the COM port

        Returns:
            str: The COM port
        """
        return self._serial.port

    @property
    def ack_bytes(self) -> bytes:
        """This method returns the ACK bytes

        Returns:
            bytes: The ACK bytes
        """
        return self._ack_bytes

    @property
    def nack_bytes(self) -> bytes:
        """This method returns the NACK bytes

        Returns:
            bytes: The NACK bytes
        """
        return self._nack_bytes
