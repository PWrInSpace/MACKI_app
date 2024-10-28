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
from src.procedures.procedure_parameters import ProcedureParameters


class ProcedurePlot(pg.LayoutWidget):
    TITLE = "Procedure"
    X_LABEL = "Time [ms]"
    Y_LABEL = "Velocity "
    PLOT_VELOCITY = "Velocity"
    PLOT_PRESSURIZATION = "Pressurization"
    PLOT_DEPRESSURIZATION = "Depressurization"
    PLOT_LIVE_VELOCITY = "Live velocity"
    VELOCITY_RANGE = [-100, 100]
    PLOTS_ELEMENTS = {
        PLOT_VELOCITY: "cyan",
        PLOT_PRESSURIZATION: "lime",
        PLOT_DEPRESSURIZATION: "magenta",
        PLOT_LIVE_VELOCITY: "white",
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

        self._y_range = self.VELOCITY_RANGE
        self._x_range = [0, 1000]

        self._plot_widget = LivePlotWidget(title=self.TITLE)
        self._plot_widget.showGrid(x=True, y=True)

        plot = self._plot_widget.getPlotItem()
        plot.setLabel(axis="bottom", text=self.X_LABEL)
        plot.setLabel(axis="left", text=self.Y_LABEL)
        plot.addLegend(offset=(0, 0))
        plot.setEnabled(False)

        self._data_connectors = {}
        for name, color in self.PLOTS_ELEMENTS.items():
            self._plot_curve = LiveLinePlot(pen=color, name=name)
            self._plot_widget.addItem(self._plot_curve)
            data_connector = DataConnector(self._plot_curve, max_points=max_points)

            self._data_connectors[name] = data_connector

        self.addWidget(self._plot_widget)

    def clear_plot(self) -> None:
        """Clear the plot."""
        for data_connector in self._data_connectors.values():
            data_connector.clear()

    def set_procedure_parameters(self, params: ProcedureParameters) -> None:
        """Set the procedure parameters to display on the plot.
            TODO: Divide this method into smaller ones.
        Args:
            params (ProcedureParameters): Procedure parameters to display.
        """
        self.clear_plot()
        time_list = params.get_time_list()
        velocity_list = params.get_velocity_list()
        velocity_range = self.VELOCITY_RANGE

        if len(time_list) > 0:
            v_min = min(velocity_list)
            v_min = v_min * 1.1 if v_min < 0 else v_min * 0.9
            v_max = max(velocity_list)
            v_max = v_max * 1.1 if v_max > 0 else v_max * 0.9
            velocity_range = [v_min, v_max]
            if v_min == v_max:
                velocity_range = [v_min - 10, v_max + 10]

            self._data_connectors[self.PLOT_VELOCITY].cb_append_data_array(
                velocity_list, time_list
            )

        if params.press_time_ms is not None:
            self._data_connectors[self.PLOT_PRESSURIZATION].cb_append_data_array(
                velocity_range, [params.press_time_ms] * 2
            )

        if params.depr_time_ms is not None:
            self._data_connectors[self.PLOT_DEPRESSURIZATION].cb_append_data_array(
                velocity_range, [params.depr_time_ms] * 2
            )

        plot = self._plot_widget.getPlotItem()
        if len(time_list) > 1:
            self._x_range = [min(time_list), max(time_list)]
        else:
            self._x_range = [0, params.press_time_ms + params.depr_time_ms]

        self._y_range = velocity_range
        plot.setXRange(self._x_range[0], self._x_range[1])
        plot.setYRange(self._y_range[0], self._y_range[1], padding=0)

    def append_live_velocity(self, velocity: float, time: float) -> None:
        """Append the live velocity to the plot.

        Args:
            velocity (float): Velocity value.
            time (float): Time value.
        """
        if time <= 0:
            return

        if time > self._data_connectors[self.PLOT_VELOCITY].x[-1]:
            return

        velocity_connector = self._data_connectors[self.PLOT_LIVE_VELOCITY]

        if velocity_connector.x and (velocity_connector.x[-1] > time):
            velocity_connector.clear()

        velocity_connector.cb_append_data_point(velocity, time)

        plot = self._plot_widget.getPlotItem()
        plot.setXRange(self._x_range[0], self._x_range[1])
        plot.setYRange(self._y_range[0], self._y_range[1], padding=0)

    def clear_live_velocity(self) -> None:
        """Clear the live velocity."""
        self._data_connectors[self.PLOT_LIVE_VELOCITY].clear()
