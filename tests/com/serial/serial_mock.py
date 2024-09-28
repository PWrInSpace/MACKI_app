from serial.tools.list_ports_common import ListPortInfo


class SerialMock:
    """Simple serial mock class for testing purposes"""

    PORTS = [ListPortInfo("COM1", True), ListPortInfo("COM2", True)]
    EMPTY_PORTS = []

    def __init__(self):
        self.is_open = False
        self.port = "COM1"
        self.available_ports = self.PORTS

    def is_connected(self):
        return self.is_open

    def set_open(self, open: bool):
        self.is_open = open

    def port(self):
        return self.port

    def set_available_ports(self, set: bool):
        if set:
            self.available_ports = self.PORTS
        else:
            self.available_ports = self.EMPTY_PORTS

    def get_available_ports(self) -> list[str]:
        return self.available_ports
