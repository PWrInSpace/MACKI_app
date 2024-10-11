from src.com.abstract import ComProtoBasic


class ComMock(ComProtoBasic):
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

    def read_until_response(self) -> str:
        return self.ACK
