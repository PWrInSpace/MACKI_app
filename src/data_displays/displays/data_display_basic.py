from PySide6.QtWidgets import QGroupBox


class DataDisplayBasic(QGroupBox):
    def __init__(self, name: str = "") -> None:
        """Initialize the DataDisplayerBasic class.

        Args:
            name (str, optional): The name of the viewer. Defaults to "".
        """
        super().__init__(name)

    def update_data(self, data_dict: dict[str, any]) -> None:
        """Update the data displayed in the viewer.

        Args:
            data_dict (dict[str, any]): A dictionary containing the data to be displayed.
            It is a key-value pair where the key is the name of the data and the value is
            the data itself.

        Raises:
            NotImplementedError: Not implemented in the subclass.
        """
        raise NotImplementedError("Method 'show' must be implemented in the subclass.")
