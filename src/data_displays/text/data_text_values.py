from src.data_displays.text.data_text_basic import DataTextBasic, logger
from src.data_displays.text.data_text_values_utils import Values, DisplayParams
from src.utils.colors import Colors


class DataTextValues(DataTextBasic):
    def __init__(self, name: str, values: Values) -> None:
        """Initializes the DataTextValues class.

        Args:
            name (str): The name of the data.
            values (Values): The values to display.
        """
        super().__init__(name)
        self._values = values

    def update_data(self, value: str) -> None:
        """ Updates the data displayed in the widget.

        Args:
            value (str): The value to display.
        """
        value = str(value)

        params = self._values[value]
        if params is None:
            params = DisplayParams(value, Colors.RED)
            logger.error(f"Value '{value}' not found in available values.")

        self._value_label.setText(params.display_value)
        self._value_label.setStyleSheet(f"color: {params.color.value}")
