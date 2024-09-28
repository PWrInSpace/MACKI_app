from dataclasses import dataclass
from src.utils.colors import Colors


@dataclass
class DisplayParams:
    display_value: str
    color: Colors


class Values:
    """Class to store a list of values with display parameters.
    It is a wrapper around a dictionary of values and their display parameters,
    which is very time efficient for lookups, because accessing a dictionary is O(1).
    """

    def __init__(
        self,
        values: list[str],
        display_values: list[str],
        colors: list[Colors],
    ) -> None:
        """Initialize the Values class.

        Args:
            values (list[str]): list of values.
            display_values (list[str]): list of values that will be displayed
            instead of the original values. If None, the original value will be displayed.
            colors (list[Colors): list of colors to display the values in.

        Raises:
            ValueError: _description_
        """
        if len(values) != len(display_values) or len(values) != len(colors):
            raise ValueError(
                "Values, display_values, and colors must have the same length."
            )

        display_params = [
            DisplayParams(val, c) for val, c in zip(display_values, colors)
        ]

        self._values = {value: params for value, params in zip(values, display_params)}

        # replace none display values with the original values
        for value, params in self._values.items():
            if params.display_value is None:
                params.display_value = value

    def __contains__(self, value: str) -> bool:
        """Check if a value is in the values list.

        Args:
            value (str): The value to check.

        Returns:
            bool: True if the value is in the values list, False otherwise.
        """
        return value in self._values

    def __getitem__(self, value: str) -> DisplayParams | None:
        """Access the display parameters for a given value.

        Args:
            value (str): The value to get the display parameters for.

        Returns:
            DisplayParams | None: The display parameters for the given value.
            None if the value is not in the values list.
        """
        return self._values.get(value, None)

    def add_value(self, value: str, display_value: str | None, color: Colors) -> None:
        """Add a new value to the values list.

        Args:
            value (str): The value to add.
            display_value (str | None): The display value for the value.
            If None, the original value will be displayed.
            color (Colors): The color to display the value in.
        """
        if value in self._values:
            raise ValueError(f"Value {value} already exists in the values list.")

        if display_value is None:
            display_value = value

        self._values[value] = DisplayParams(display_value, color)
