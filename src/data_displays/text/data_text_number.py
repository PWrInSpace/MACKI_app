from src.data_displays.text.data_text_basic import DataTextBasic

from src.utils.colors import Colors


class DataTextNumber(DataTextBasic):
    def __init__(
        self, name: str, lower_bound: float = None, upper_bound: float = None
    ) -> None:
        super().__init__(name)

        self._lower_bound = float("-inf") if lower_bound is None else lower_bound
        self._upper_bound = float("inf") if upper_bound is None else upper_bound

        if self._lower_bound > self._upper_bound:
            raise ValueError("Lower bound must be less than or equal to upper bound.")

    def update_data(self, value: int | float) -> None:
        if self._lower_bound <= value <= self._upper_bound:
            color = Colors.WHITE
        else:
            color = Colors.RED

        if isinstance(value, int):
            self._value_label.setText(str(value))
        else:
            self._value_label.setText(f"{value:.2f}")

        self._value_label.setStyleSheet(f"color: {color.value}")
