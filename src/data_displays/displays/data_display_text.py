from PySide6.QtWidgets import QGridLayout, QFrame

from src.data_displays.displays.data_display_basic import DataDisplayBasic, logger
from src.data_displays.text.data_text_basic import DataTextBasic


class DataDisplayText(DataDisplayBasic):
    def __init__(
        self,
        data_display_config: list[DataTextBasic],
        name: str = "",
        col_num: int = 3
    ) -> None:
        """ Initializes the DataDisplayText class.

        Args:
            data_display_config (list[DataTextBasic]): A list of data display widgets.
            name (str, optional): The name of the data display. Defaults to "".
            col_num (int, optional): The number of columns to display the data in. Defaults to 3.
        """
        super().__init__(name)
        self._col_num = col_num
        self._display_config_dict = {display.name: display for display in data_display_config}

        self._init_ui()

    def _init_ui(self) -> None:
        """ Initializes the user interface for the data display.
        """
        layout = QGridLayout()

        row_num = 0
        for i, data_text in enumerate(self._display_config_dict.values()):
            col = (i % self._col_num) * 2
            layout.addWidget(data_text, row_num, col)

            if i % self._col_num == self._col_num - 1:
                row_num += 1
            else:
                vline = QFrame()
                vline.setFrameShape(QFrame.VLine)  # Set to vertical line
                vline.setFrameShadow(QFrame.Sunken)
                layout.addWidget(vline, row_num, col + 1)

        self.setLayout(layout)

    def update_data(self, data_dict: dict[str, any]) -> None:
        """ Updates the data displayed in the widgets.

        Args:
            data_dict (dict[str, any]): A dictionary containing the data to be displayed.
        """
        for name, value in data_dict.items():
            data_text = self._display_config_dict.get(name, None)

            if data_text is not None:
                data_text.update_data(value)
            else:
                logger.error(f"Data display '{name}' not found in display config.")
