class ComProtoBasic:
    ACK = "ACK"
    NACK = "NACK"

    def connect(self):
        """Connect to the device"""
        raise NotImplementedError("Method not implemented")

    def disconnect(self):
        """Disconnect from the device"""
        raise NotImplementedError("Method not implemented")

    def write(self, data: str):
        """Write data to the device

        Args:
            data (str): data to write
        """
        raise NotImplementedError("Method not implemented")

    def write_and_check(self, data: str):
        """Write data to the device and check the response

        Args:
            data (str): data to write
        """
        raise NotImplementedError("Method not implemented")

    def read(self):
        """Read data from the device"""
        raise NotImplementedError("Method not implemented")

    def is_connected(self):
        """Check if the device is connected"""
        raise NotImplementedError("Method not implemented")

    def read_until_response(self):
        """Read until a response is received"""
        raise NotImplementedError("Method not implemented")
