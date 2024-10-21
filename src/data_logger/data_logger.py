import os
from typing import Any
from datetime import datetime
from src.data_parser import DataParser
import logging

logger = logging.getLogger("data_logger")


class DataLogger:
    BASE_FOLDER = "data"
    DATA_FILE_NAME = "data.csv"
    PROCEDURE_PROFILE_NAME = "procedure.csv"

    def __init__(self, data_parser: DataParser):
        """Initializes the DataLogger object with the data parser

        Args:
            data_parser (DataParser): data parser for which the data will be stored
        """
        self._data_names = data_parser.data_names

        if not os.path.isdir(self.BASE_FOLDER):
            os.makedirs(self.BASE_FOLDER)

        self._data_folder = os.path.join(self.BASE_FOLDER, self._get_current_time())
        os.makedirs(self._data_folder)

        self._data_file = os.path.join(self._data_folder, self.DATA_FILE_NAME)
        self._write_header_to_file(self._data_file)

        self._procedure_folder = None
        self._procedure_data_file = None

    def _get_current_time(self) -> str:
        """Returns the current time in the format YYYY-MM-DD_HH-MM-SS-MS

        Returns:
            str: Current time
        """
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def _write_header_to_file(self, file_path):
        """Writes the header to the data file
        """
        with open(file_path, "w") as file:
            file.write("datetime;")
            file.write(";".join(self._data_names) + "\n")

    def _write_data_to_file(self, file_path: str, data_list: list[str]) -> None:
        """Writes the data to the data file

        Args:
            file_path (str): File path
            data_list (list[str]): Data to be written
        """
        with open(file_path, "a") as file:
            file.write(self._get_current_time() + ";")
            file.write(";".join(data_list) + "\n")

    def add_data(self, data_dict: dict[str, Any]) -> None:
        """Adds the data to the data file

        Args:
            data_dict (dict[str, Any]): Data to be added
        """
        try:
            data = [str(data_dict[name]) for name in self._data_names]
        except KeyError:
            logger.error("Invalid data dictionary")
        else:
            self._write_data_to_file(self._data_file, data)

            if self._procedure_data_file:
                self._write_data_to_file(self._procedure_data_file, data)

    def create_procedure_logger(self, procedure_name: str = "") -> None:
        """Creates a procedure logger

        Args:
            procedure_name (str, optional): Procedure name. Defaults to "".
        """
        self._procedure_folder = self._get_current_time() + "_" + procedure_name
        self._procedure_folder = os.path.join(self._data_folder, self._procedure_folder)
        os.makedirs(self._procedure_folder)

        self._procedure_data_file = os.path.join(self._procedure_folder, self.DATA_FILE_NAME)
        self._write_header_to_file(self._procedure_data_file)

    def remove_procedure_logger(self) -> None:
        """Removes the procedure logger
        """
        self._procedure_folder = None
        self._procedure_data_file = None

    @property
    def procedure_folder(self) -> str:
        """Returns the procedure folder

        Returns:
            str: Procedure folder
        """
        return self._procedure_folder

    @property
    def procedure_profile_file(self) -> str:
        """Returns the procedure file

        Returns:
            str: Procedure file
        """
        if not self._procedure_folder:
            return ""

        return os.path.join(self._procedure_folder, self.PROCEDURE_PROFILE_NAME)
