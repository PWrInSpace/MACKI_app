import json
import struct
import logging
from typing import Self

logger = logging.getLogger("parser")


class DataParser:
    def __init__(self, format_string: str, data_names: list[str]):
        """Initializes the DataParser object with the format string and data keys

        Args:
            format_string (str): format string for the struct.unpack method.
            The first character of the format string must be the byte order.
            To more information, see https://docs.python.org/3/library/struct.html#format-strings
            data_names (list[str]): Data keys to be used in the dictionary returned by the parse
            method

        Raises:
            ValueError: If the length of the format string and data keys are different
            struct.error: If the format string is invalid
        """
        # Skip the first character, which is the byte order
        if len(format_string[1:]) != len(data_names):
            raise ValueError("Format string and data keys must have the same length")

        # check the string format, if is invalid, raise an struct.error
        struct.calcsize(format_string)

        self._format = format_string
        self._data_keys = data_names

    def parse(self, data: bytes) -> dict:
        """Parses the data bytes using the format string and data keys

        Args:
            data (bytes): Data to be parsed

        Returns:
            dict: Dictionary with the data keys and the parsed values,
            if the length of the data does not match the format string,
            an empty dictionary is returned
        """
        if len(data) != struct.calcsize(self._format):
            logger.error("Data length does not match the format string")
            return {}

        unpacked_data = struct.unpack(self._format, data)

        data_dict = {key: value for key, value in zip(self._data_keys, unpacked_data)}

        return data_dict

    @staticmethod
    def from_json(json_file: str) -> Self:
        """Creates a DataParser object from a json file

        Args:
            json_file (str): Path to the json file with the format and data keys

        Returns:
            Self: DataParser object created from the json file
        """
        with open(json_file, "r") as file:
            json_data = json.load(file)

        return DataParser(json_data["format"], json_data["data_names"])
