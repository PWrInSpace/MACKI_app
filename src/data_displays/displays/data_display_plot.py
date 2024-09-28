import json
from typing import Any, Self
from PySide6.QtWidgets import QGridLayout

from src.data_displays import DataDisplayBasic
from src.data_displays.plot.data_plot import DataPlot


class DataDisplayPlot(DataDisplayBasic):
    def __init__(self, plots: list[DataPlot], name: str = "", col_num: int = 2) -> None:
        """Initialize the DataTextBasic class.

        Args:
            plots (list[DataPlot]): A list of data plots to display.
            name (str, optional): The name of the viewer. Defaults to "".
            col_num (int, optional): The number of columns to display the data in. Defaults to 2.
        """
        super().__init__(name)

        self._plots = plots
        self._col_num = col_num
        self._init_ui()

    def _init_ui(self) -> None:
        """Initializes the user interface for the data display."""
        layout = QGridLayout()

        # TODO: Stretch the last row to fill the remaining columns
        row_num = 0
        for i, plot in enumerate(self._plots):
            layout.addWidget(plot, row_num, i % self._col_num)

            if i % self._col_num == self._col_num - 1:
                row_num += 1

        self.setLayout(layout)

    def update_data(self, data: dict[str, Any]) -> None:
        """Update the data displayed in the viewer.

        Args:
            data (any): The data to be displayed.
        """
        for plot in self._plots:
            if plot.x_name in data and plot.y_name in data:
                plot.add_data(data[plot.x_name], data[plot.y_name])

    @staticmethod
    def from_JSON(json_file: str) -> Self:
        """Create a DataDisplayPlot object from a JSON file.

        Args:
            json_file (str): The path to the JSON file.

        Returns:
            Self: The DataDisplayPlot object.
        """
        with open(json_file, "r") as file:
            data = json.load(file)

        group_name = data.get("name", "")
        col_num = data.get("col_num", 2)

        plots = []
        for plot_data in data.get("plots", {}):
            x_name = plot_data.get("x_name", "")
            y_name = plot_data.get("y_name", "")
            title = plot_data.get("title", "")
            color = plot_data.get("color", "lime")
            max_points = plot_data.get("max_points", 200)
            x_label = plot_data.get("x_label", "")
            y_label = plot_data.get("y_label", "")

            plot = DataPlot(x_name, y_name, title, color, max_points, x_label, y_label)
            plots.append(plot)

        return DataDisplayPlot(plots, group_name, col_num)
