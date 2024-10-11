from typing import Any
import json
from typing import Self
from PySide6.QtWidgets import QGridLayout, QFrame

from src.data_displays.displays.data_display_basic import DataDisplayBasic, logger
from src.data_displays.text.data_text_basic import DataTextBasic
from src.data_displays.text.data_text_number import DataTextNumber
from src.data_displays.text.data_text_values import DataTextValues
from src.data_displays.text.data_text_values_utils import ValuesConfig

from src.utils.colors import Colors


class DataDisplayText(DataDisplayBasic):
    def __init__(
        self, data_display_config: list[DataTextBasic], name: str = "", col_num: int = 3
    ) -> None:
        """Initializes the DataDisplayText class.

        Args:
            data_display_config (list[DataTextBasic]): A list of data display widgets.
            name (str, optional): The name of the data display. Defaults to "".
            col_num (int, optional): The number of columns to display the data in. Defaults to 3.
        """
        super().__init__(name)
        self._col_num = col_num
        self._display_configs = {
            display.name: display for display in data_display_config
        }

        self._init_ui()

    def _init_ui(self) -> None:
        """Initializes the user interface for the data display."""
        layout = QGridLayout()

        row_num = 0
        for i, data_text in enumerate(self._display_configs.values()):
            col = (i % self._col_num) * 2
            layout.addWidget(data_text, row_num, col)

            if i % self._col_num != self._col_num - 1:
                vline = QFrame()
                vline.setFrameShape(QFrame.VLine)  # Set to vertical line
                vline.setFrameShadow(QFrame.Sunken)
                layout.addWidget(vline, row_num, col + 1)
            else:
                # end of row go to next row
                row_num += 1

        self.setLayout(layout)

    def update_data(self, data_dict: dict[str, any]) -> None:
        """Updates the data displayed in the widgets.

        Args:
            data_dict (dict[str, any]): A dictionary containing the data to be displayed.
        """
        for name, value in data_dict.items():
            data_text = self._display_configs.get(name, None)

            if data_text is not None:
                data_text.update_data(value)

    @staticmethod
    def from_JSON(json_file: str) -> Self:
        """Creates a DataDisplayText object from a JSON file.

        Args:
            json_file (str): The path to the JSON file.

        Returns:
            Self: The DataDisplayText object.
        """
        decoder = _JSONDeserializer(json_file)
        return decoder.decode()


class _JSONDeserializer:
    DEFAULT_COLOR = "white"

    def __init__(self, json_file: str) -> None:
        """Initializes the JSONDecoder class.

        Args:
            json_file (str): The path to the JSON file.
        """
        self._json_file = json_file

    def _parse_data_text_number_dict(self, cfg_dict: dict[str, Any]) -> DataTextNumber:
        """Parses a dictionary for a DataTextNumber object.

        Args:
            cfg_dict (dict[str, Any]): The dictionary to parse.

        Returns:
            DataTextNumber: The DataTextNumber object.
        """
        name = cfg_dict["name"]
        lower_bound = cfg_dict.get("lower_bound", None)
        upper_bound = cfg_dict.get("upper_bound", None)

        return DataTextNumber(name, lower_bound, upper_bound)

    def _parse_data_text_values_dict(self, cfg_dict: dict[str, Any]) -> DataTextValues:
        """Parses a dictionary for a DataTextValues object.

        Args:
            cfg_dict (dict[str, Any]): The dictionary to parse.

        Raises:
            ValueError: Enum and colors enum must have the same length.

        Returns:
            DataTextValues: The DataTextValues object.
        """
        name = cfg_dict["name"]
        enum = cfg_dict["enum"]
        colors_enum = cfg_dict.get(
            "enum_colors", {k: self.DEFAULT_COLOR for k in enum.keys()}
        )

        if len(enum) != len(colors_enum):
            raise ValueError("Enum and colors enum must have the same length.")

        values = list(enum.keys())
        display_values = list(enum.values())
        colors = [colors_enum[v] for v in values]  # sort colors by values
        app_colors = [
            Colors[color.upper()] for color in colors
        ]  # Convert to app colors

        values_cfg = ValuesConfig(values, display_values, app_colors)

        return DataTextValues(name, values_cfg)

    def _parse_data_text_basic_dict(self, cfg_dict: dict[str, Any]) -> DataTextBasic:
        """Parses a dictionary for a DataTextBasic object.

        Args:
            cfg_dict (dict[str, Any]): The dictionary to parse.

        Returns:
            DataTextBasic: The DataTextBasic object.
        """
        name = cfg_dict["name"]

        return DataTextBasic(name)

    def _data_config_from_json_dict(
        self, json_dict: dict[str, Any]
    ) -> list[DataTextBasic]:
        """Converts a JSON dictionary to a list of DataTextBasic objects.

        Args:
            json_dict (dict[str, Any]): The JSON dictionary.

        Returns:
            list[DataTextBasic]: The list of DataTextBasic objects.
        """
        data_list = json_dict["data"]

        configs = []
        for data in data_list:
            if "enum" in data:
                data_config = self._parse_data_text_values_dict(data)
            elif ("lower_bound" in data) or ("upper_bound" in data):
                data_config = self._parse_data_text_number_dict(data)
            else:
                data_config = self._parse_data_text_basic_dict(data)

            configs.append(data_config)

        return configs

    def _json_dict_to_DataDisplayText(
        self, json_dict: dict[str, Any]
    ) -> DataDisplayText:
        """Converts a JSON dictionary to a DataDisplayText object.

        Args:
            json_dict (dict[str, Any]): The JSON dictionary.

        Returns:
            DataDisplayText: The DataDisplayText object.
        """
        object_name = json_dict["name"]
        col_num = json_dict["col_num"]

        data_config = self._data_config_from_json_dict(json_dict)

        return DataDisplayText(data_config, object_name, col_num)

    def decode(self) -> Self:
        """Decodes the JSON file into a DataDisplayText object.

        Returns:
            Self: The DataDisplayText object.
        """
        with open(self._json_file, "r") as file:
            data = json.load(file)

        return self._json_dict_to_DataDisplayText(data)
