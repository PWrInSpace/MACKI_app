from src.data_viewers.text.data_text_basic import DataTextBasic
from src.data_viewers.text.data_text_values_utils import Values, DisplayParams
from src.utils.colors import Colors


class DataTextValues(DataTextBasic):
    def __init__(self, name: str, values: Values) -> None:
        super().__init__(name)
        self._values = values

    def update_data(self, value: str) -> None:
        params = self._values[value]
        if params is None:
            params = DisplayParams(value, Colors.RED)

        self._value_label.setText(params.display_value)
        self._value_label.setStyleSheet(f"color: {params.color.value}")
