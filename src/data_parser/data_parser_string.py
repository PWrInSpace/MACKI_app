import json
import logging
from enum import Enum
from typing import Self

logger = logging.getLogger("parser")


class ParserFormats(Enum):
    """Enum with the available format characters for the DataParserString class"""

    INT = "i"
    FLOAT = "f"


class DataParserString:
    DELIMITER = ";"

    def __init__(self, format_string: str, data_names: list[str]):
        """DataParserString constructor initializes the format string and data keys
        Available format characters are specified in the ParserFormats enum

        Args:
            format_string (str): format string with the format characters
            data_names (list[str]): data names to be used as keys in the parsed data

        Raises:
            ValueError: If the format string and data keys have different lengths
        """

        # Skip the first character, which is the byte order
        if len(format_string) != len(data_names):
            raise ValueError("Format string and data keys must have the same length")

        self._format = format_string
        self._data_keys = data_names

        self._prefix = ""
        self._postfix = ""

        self._check_format()

    def set_prefix(self, prefix: str) -> None:
        """Sets a prefix to the data keys

        Args:
            prefix (str): Prefix to be added to the data keys
        """
        self._prefix = prefix

    def set_postfix(self, postfix: str) -> None:
        """Sets a postfix to the data keys

        Args:
            postfix (str): Postfix to be added to the data keys
        """
        self._postfix = postfix

    def _extract_data_string(self, data: str) -> str:
        """Extracts the data string from the data bytes

        Args:
            data (str): Data bytes to be extracted

        Returns:
            str: Data string extracted from the data bytes
        """
        data_string = data.replace(self._prefix, "")
        data_string = data_string.replace(self._postfix, "")

        if data_string.endswith(";"):
            data_string = data_string[:-1]

        return data_string

    def _check_format(self) -> None:
        for format_char in self._format:
            if format_char not in (format_.value for format_ in ParserFormats):
                raise ValueError(f"Invalid format character: {format_char}")

    def parse(self, data: str) -> dict:
        """Parses the data bytes using the format string and data keys

        Args:
            data (bytes): Data to be parsed

        Returns:
            dict: Dictionary with the data keys and the parsed values,
            if the length of the data does not match the format string,
            an empty dictionary is returned
        """
        data = self._extract_data_string(data)

        data_list = data.split(self.DELIMITER)
        if len(data_list) != len(self._data_keys):
            logger.error("Invalid number of data")
            return {}

        data_dict = {}
        for single_data, key, format_char in zip(
            data_list, self._data_keys, self._format
        ):
            match format_char:
                case ParserFormats.INT.value:
                    data_dict[key] = int(single_data)
                case "f":
                    data_dict[key] = float(single_data)
                case ParserFormats.FLOAT.value:
                    raise RuntimeError("Invalid data format")

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

        return DataParserString(json_data["format"], json_data["data_names"])

    @property
    def data_names(self) -> list[str]:
        """Returns the data keys of the DataParser object

        Returns:
            List[str]: List of data keys (data names)
        """
        return self._data_keys

    # @property
    # def frame_size(self) -> int:
    #     return self._frame_size
