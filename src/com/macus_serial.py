from typing import override
import serial
import serial.tools.list_ports

from serial.serialutil import PortNotOpenError, SerialException

from src.com.com_proto_basic import ComProtoBasic


class MacusSerial(ComProtoBasic):
    EOF = "\r\n"
    BAUDRATE = 115200
    READ_TIMEOUT_S = 0.1
    WRITE_TIMEOUT_S = 0.1

    ACK = "ACK"
    NACK = "NACK"

    def __init__(self, com_port: str = None) -> None:
        """This method initializes the MacusSerial class

        Args:
            com_port (str, optional): com port to connect to. Defaults to None.
        """
        super().__init__()
        self._serial = serial.Serial()
        self._serial.port = com_port
        self._serial.baudrate = self.BAUDRATE
        self._serial.timeout = self.READ_TIMEOUT_S
        self._serial.write_timeout = self.WRITE_TIMEOUT_S

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
        if not self._serial.is_open:
            raise PortNotOpenError()

        if not data.endswith(self.EOF):
            data += self.EOF

        self._serial.write(data.encode())

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
        if not self._serial.is_open:
            raise PortNotOpenError()

        self._serial.timeout = read_timeout_s
        response = self._serial.read_until(self.EOF.encode())

        return response.decode().strip()

    @override
    def is_connected(self) -> bool:
        """This method checks if the device is connected

        Returns:
            bool: True if the device is connected, False otherwise
        """
        return self._serial.is_open

    def get_available_ports(self) -> list[str]:
        """This method lists the available COM ports

        Returns:
            list[str]: The list of available COM ports
        """
        return serial.tools.list_ports.comports()

    # def read_response(self) -> str:
    #     """ This method reads the response from the device

    #     Returns:
    #         str: The response from the device
    #     """
    #     response = self.read()

    #     if self.ACK in response:
    #         response = response.replace(self.ACK, "")
    #     elif self.NACK in response:
    #         raise SerialException(f"NACK received: {response}")
    #     else:
    #         raise SerialException(f"Invalid response: {response}")

    #     return response

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
