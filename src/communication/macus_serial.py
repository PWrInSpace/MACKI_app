from typing import override
import serial
from serial.serialutil import PortNotOpenError, SerialException
from serial.serialutil import Timeout

from src.communication.communication_protocol_basic import CommunicationProtocolBasic


class MacusSerial(CommunicationProtocolBasic):
    EOF = "\r\n"
    BAUDRATE = 115200
    READ_TIMEOUT_S = 0.1
    WRITE_TIMEOUT_S = 0.1

    ACK = "ACK"
    NACK = "NACK"

    def __init__(self, com_port: str = None) -> None:
        super().__init__()
        self._serial = serial.Serial()
        self._serial.port = com_port
        self._serial.baudrate = self.BAUDRATE
        self._serial.timeout = self.READ_TIMEOUT_S
        self._serial.write_timeout = self.WRITE_TIMEOUT_S

    @override
    def connect(self, com_port: str = None) -> None:
        if self._serial.is_open:
            raise SerialException("Serial port is already open")

        self._serial.port = com_port or self._serial.port
        if not self._serial.port:
            raise ValueError("COM port not provided")

        self._serial.open()

    @override
    def disconnect(self) -> None:
        if not self._serial.is_open:
            raise PortNotOpenError("Serial port is not open")

        self._serial.close()

    @override
    def write(self, data: str) -> None:
        if not self._serial.is_open:
            raise PortNotOpenError("Serial port is not open")

        if not data.endswith(self.EOF):
            data += self.EOF

        self._serial.write(data.encode())

    @override
    def read(self, read_timeout_s: float = 0.1) -> str:
        if not self._serial.is_open:
            raise PortNotOpenError("Serial port is not open")

        self._serial.timeout = read_timeout_s
        response = self._serial.read_until(self.EOF.encode())

        return response.decode().strip()

    @override
    def is_connected(self) -> bool:
        return self._serial.is_open

    def read_response(self) -> str:
        """ This method reads the response from the device

        Returns:
            str: The response from the device
        """
        response = self.read()

        if self.ACK in response:
            response = response.replace(self.ACK, "")
        elif self.NACK in response:
            raise SerialException(f"NACK received: {response}")
        else:
            raise SerialException(f"Invalid response: {response}")

        return response

    def write_command(self, command_name: str, *argv) -> str:
        """ This method writes a command to the serial port and reads the response

        Args:
            command_name (str): The command to write

        Returns:
            str: The response from the device
        """
        command = command_name

        for arg in argv:
            command += f" {arg}"

        self.write(command)

        return self.read_response()
