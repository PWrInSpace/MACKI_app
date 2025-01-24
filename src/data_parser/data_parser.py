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

        self._postfix = b""
        self._prefix = b""
        self._postfix_len = 0
        self._prefix_len = 0

        self._update_frame_size()

    def _update_frame_size(self) -> None:
        self._frame_size = self._prefix_len
        self._frame_size += struct.calcsize(self._format)
        self._frame_size += self._postfix_len

    def set_prefix(self, prefix: bytes) -> None:
        """Set prefix

        Args:
            prefix (bytes): prefix in bytes
        """
        self._prefix = prefix
        self._prefix_len = len(self._prefix)
        self._update_frame_size()

    def set_postfix(self, postfix: bytes) -> None:
        """Set postifx

        Args:
            postfix (bytes): postfix in bytes
        """
        self._postfix = postfix
        self._postfix_len = len(self._postfix)
        self._update_frame_size()

    def _extract_data(self, data) -> bytes:
        if len(data) != self._frame_size:
            logger.error("Invalid data size")
            return b""

        return data[self._prefix_len : -self._postfix_len]

    def parse(self, data: bytes) -> dict:
        """Parses the data bytes using the format string and data keys

        Args:
            data (bytes): Data to be parsed

        Returns:
            dict: Dictionary with the data keys and the parsed values,
            if the length of the data does not match the format string,
            an empty dictionary is returned
        """
        # print(data)
        extracted_data = data
        # extracted_data = self._extract_data(data)
        if len(extracted_data) != struct.calcsize(self._format):
            logger.error(
                f"Data length does not match the format string, {extracted_data}, "
                f"extracted_data len {len(extracted_data)}, size {struct.calcsize(self._format)}"
            )
            return {}

        unpacked_data = struct.unpack(self._format, extracted_data)

        data_dict = {key: value for key, value in zip(self._data_keys, unpacked_data)}
        print(data_dict)

        return data_dict

    @staticmethod
    def from_JSON(json_file: str) -> Self:
        """Creates a DataParser object from a json file

        Args:
            json_file (str): Path to the json file with the format and data keys

        Returns:
            Self: DataParser object created from the json file
        """
        with open(json_file, "r") as file:
            json_data = json.load(file)

        return DataParser(json_data["format"], json_data["data_names"])

    @property
    def data_names(self) -> list[str]:
        """Returns the data keys of the DataParser object

        Returns:
            List[str]: List of data keys (data names)
        """
        return self._data_keys

    @property
    def frame_size(self) -> int:
        return self._frame_size
