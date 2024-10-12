"""
Plots should be moved to separate folder, to avoid redundancy and to make 
the code more readable. Now the data display and procedure uses plots.
But they are created differently. The plots should be created in the same way.

Due to the lack of time, here is another implementation of the live plot but for
the procedures.
"""
import pyqtgraph as pg
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget

class ProcedurePlot(pg.LayoutWidget):
    TITLE = "Procedure Plot"
    X_LABEL = "Time [s]"
    PLOT_VELOCITY = "Velocity"
    PLOT_PRESSURIZATION = "Pressurization"
    PLOT_DEPRESSURIZATION = "Depressurization"
    PLOT_LIVE_VELOCITY = "Live_velocity"
    PLOTS_ELEMENTS = {
        PLOT_VELOCITY: "cyan",
        PLOT_PRESSURIZATION: "lime",
        PLOT_DEPRESSURIZATION: "magenta",
        PLOT_LIVE_VELOCITY: "gray"
    }

    def __init__(
        self,
        max_points: int = 500,
    ) -> None:
        """Initialize the LivePlot class.

        Args:
            max_points (int, optional): max points stored on plot. Defaults to 200.
        """
        super().__init__()

        self._plot_widget = LivePlotWidget(title=self.TITLE)
        self._plot_widget.showGrid(x=True, y=True)

        plot = self._plot_widget.getPlotItem()
        plot.setLabel(axis="bottom", text=self.X_LABEL, )
        plot.addLegend(offset=(0, 0))

        self._data_connectors = {}
        for name, color in self.PLOTS_ELEMENTS.items():
            self._plot_curve = LiveLinePlot(pen=color, name=name)
            self._plot_widget.addItem(self._plot_curve)
            data_connector = DataConnector(self._plot_curve, max_points=max_points)

            self._data_connectors[name] = data_connector

        self.addWidget(self._plot_widget)

        self._data_connectors[self.PLOT_PRESSURIZATION].cb_append_data_array(
            [20, -0], [4, 4]
        )
        self._data_connectors[self.PLOT_DEPRESSURIZATION].cb_append_data_array(
            [20, -0], [8, 8]
        )

        self._data_connectors[self.PLOT_LIVE_VELOCITY].cb_append_data_array(
            [5, 4.5, 5.5, 5], [0, 2, 3, 5]
        )

        self._data_connectors[self.PLOT_VELOCITY].cb_append_data_array(
            [5, 5, 10, 10], [0, 5, 5, 10]
        )

        plot.setXRange(0, 10)
        plot.setYRange(5, 10, padding=0.2)