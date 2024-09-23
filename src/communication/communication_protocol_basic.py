from abc import ABC, abstractmethod


class CommunicationProtocolBasic(ABC):
    @abstractmethod
    def connect(self):
        """Connect to the device"""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the device"""
        pass

    @abstractmethod
    def write(self, data: str):
        """Write data to the device

        Args:
            data (str): data to write
        """
        pass

    @abstractmethod
    def read(self):
        """Read data from the device"""
        pass

    @abstractmethod
    def is_connected(self):
        """Check if the device is connected"""
        pass
