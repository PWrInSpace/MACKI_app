import pyqtgraph as pg
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget


class LivePlot(pg.LayoutWidget):
    def __init__(
        self,
        title: str = "",
        color: str = "lime",
        max_points: int = 200,
        x_label: str = "",
        y_label: str = "",
    ) -> None:
        """Initialize the LivePlot class.

        Args:
            title (str, optional): Plot title. Defaults to "".
            color (str, optional): Line color. Defaults to "lime".
            max_points (int, optional): max points stored on plot. Defaults to 200.
            x_label (str, optional): x label. Defaults to "".
            y_label (str, optional): y_label. Defaults to "".
        """
        super().__init__()

        self._plot_widget = LivePlotWidget(title=title)
        self._plot_widget.showGrid(x=True, y=True)
        self._plot_curve = LiveLinePlot(pen=color)
        self._plot_widget.addItem(self._plot_curve)
        self._data_connector = DataConnector(self._plot_curve, max_points=max_points)

        if x_label:
            self.set_x_label(x_label)

        if y_label:
            self.set_y_label(y_label)

        self.addWidget(self._plot_widget)

    def set_x_label(self, label: str) -> None:
        """Set the x label of the plot.

        Args:
            label (str): The x label of the plot.
        """
        plot = self._plot_widget.getPlotItem()
        plot.setLabel(axis="bottom", text=label)

    def set_y_label(self, label: str) -> None:
        """Set the y label of the plot.

        Args:
            label (str): The y label of the plot.
        """
        plot = self._plot_widget.getPlotItem()
        plot.setLabel(axis="left", text=label)

    @property
    def data_connector(self):
        """Get the data connector of the plot.

        Returns:
            Unknown: The data connector of the plot.
        """
        return self._data_connector
