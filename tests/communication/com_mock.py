from src.communication import CommunicationProtocolBasic


class ComMock(CommunicationProtocolBasic):
    def __init__(self):
        self.last_write = None
        self.write_count = 0

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def write(self, message: str) -> None:
        self.last_write = message
        self.write_count += 1

    def read(self) -> str:
        pass

    def is_connected(self) -> bool:
        pass
