import logging
from src.data_displays.plot.live_plot import LivePlot

logger = logging.getLogger("data_plot")


class DataPlot(LivePlot):
    def __init__(
        self,
        x_name: str,
        y_name: str,
        title: str = "",
        color: str = "lime",
        max_points: int = 200,
        x_label: str = "",
        y_label: str = "",
    ) -> None:
        """ Initialize the DataPlot class.

        Args:
            x_name (str): name of received data to be plotted on x axis.
            y_name (str): name of received data to be plotted on y axis.
            title (str, optional): Plot title. Defaults to "".
            color (str, optional): Line color. Defaults to "lime".
            max_points (int, optional): max points stored on plot. Defaults to 200.
            x_label (str, optional): x label. Defaults to "".
            y_label (str, optional): y_label. Defaults to "".
        """
        self._x_name = x_name
        self._y_name = y_name
        super().__init__(title, color, max_points, x_label, y_label)

    def add_data(self, data_x: int | float, data_y: int | float) -> None:
        """ Add a data point to the plot.

        Args:
            data_x (int | float): The x value of the data point.
            data_y (int | float): The y value of the data point.
        """
        if not isinstance(data_y, (int, float)):
            logger.error(f"Data point {data_y} is not a number.")

        if not isinstance(data_x, (int, float)):
            logger.error(f"Data point {data_x} is not a number.")

        self._data_connector.cb_append_data_point(data_y, data_x)

    @property
    def x_name(self) -> str:
        """Get the name (key) of x axis data.

        Returns:
            str: The x name of the plot.
        """
        return self._x_name

    @property
    def y_name(self) -> str:
        """Get the name (key) of y axis data.

        Returns:
            str: The y name of the plot.
        """
        return self._y_name
