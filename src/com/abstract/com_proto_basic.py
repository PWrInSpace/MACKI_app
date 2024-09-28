class ComProtoBasic:
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

    def read(self):
        """Read data from the device"""
        raise NotImplementedError("Method not implemented")

    def is_connected(self):
        """Check if the device is connected"""
        raise NotImplementedError("Method not implemented")
