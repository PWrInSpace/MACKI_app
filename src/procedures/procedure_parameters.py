import logging
from typing import Self, Any
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger("procedure_parameters")


@dataclass
class ProcedureParameters:
    """
    Data class for procedure parameters.
    """
    KEY_NAME = "name"
    KEY_PRESS = "pressurization"
    KEY_DEPR = "depressurization"
    KEY_TIME_PROFILE = "time_profile"
    KEY_VELOCITY_PROFILE = "velocity_profile"

    MAX_VELOCITY = 100_000
    MIN_VELOCITY = -100_000
    TIME_IDX = 0
    VELOCITY_IDX = 1

    # The name of the procedure.
    name: str
    # The velocity profile of the procedure., list of tuples (time, velocity)
    velocity_profile: list[tuple[float, float]] | None
    # The time of pressurization of the system.
    press_time_ms: float | None
    # The time of depressurization of the system.
    depr_time_ms: float | None
    # # The time of the procedure.
    skip_check: bool = False

    def _initial_check(self) -> bool:
        """
        Initial check of the parameters.
        """
        if self.name is None:
            raise ValueError("The name of the procedure is None.")

        if self.velocity_profile is not None and\
           not isinstance(self.velocity_profile, list):
            raise ValueError("The velocity profile is not a list.")

        if self.press_time_ms is not None and\
           not isinstance(self.press_time_ms, (int, float)):
            raise ValueError("The pressurization time is not a number.")

        if self.depr_time_ms is not None and\
           not isinstance(self.depr_time_ms, (int, float)):
            raise ValueError("The depressurization time is not a number.")

    def _check_dependencies(self):
        if self.velocity_profile is None and\
           (self.press_time_ms is None or self.depr_time_ms is None):
            raise ValueError(
                "The velocity profile is None and the press or depress time is None."
            )

        if self.press_time_ms is not None and self.depr_time_ms is None:
            raise ValueError("The pressurization time is set but not the depressurization.")

        if self.press_time_ms is None and self.depr_time_ms is not None:
            raise ValueError("The depressurization time is set but not the pressurization.")

        if self.press_time_ms is not None and self.depr_time_ms is not None:
            if self.press_time_ms < 0 or self.depr_time_ms < 0:
                raise ValueError("Pressurization or depressurization time is negative.")

        if self.press_time_ms is not None and self.depr_time_ms is not None:
            if self.press_time_ms > self.depr_time_ms:
                raise ValueError("Press time is greater than depress time.")

    def _check_velocity_profile(self) -> bool:
        """
        Check if the velocity profile is valid.
        """
        # We can have an empty velocity profile (only pressurization and depressurization).
        if self.velocity_profile is None:
            return True

        if len(self.velocity_profile) == 0:
            self.velocity_profile = None
            logger.warning("The velocity profile is empty, setting it to None.")
            return True

        # Check if the velocity profile is sorted by time.
        for i in range(len(self.velocity_profile) - 1):
            if self.velocity_profile[i][self.TIME_IDX] > self.velocity_profile[i + 1][self.TIME_IDX]:
                raise ValueError("The velocity profile is not sorted by time.")

        # Check the velocity values
        for time, velocity in self.velocity_profile:
            if time < 0:
                raise ValueError("Time is negative.")

            if velocity < self.MIN_VELOCITY or velocity > self.MAX_VELOCITY:
                raise ValueError(
                    f"Velocity is out of range ({self.MIN_VELOCITY}, {self.MAX_VELOCITY})."
                )

        return True

    def _check_time_param(self, param: float) -> bool:
        """
        Check if the Time param is valid.
        """
        if param is None:
            return True

        if param < 0:
            raise ValueError("Time param is negative.")

        if param > self.velocity_profile[-1][self.TIME_IDX]:
            raise ValueError("Time param is greater than the total time of the procedure.")

        return True

    def _add_end_of_procedure(self):
        """ Add the end of the procedure to the velocity profile, which is
        a velocity of 0 at the end of the procedure.
        If the procedure is already at 0 velocity at the end, do nothing.
        """
        if not self.velocity_profile:
            return

        if self.velocity_profile[-1][self.VELOCITY_IDX] != 0:
            self.velocity_profile.append((self.velocity_profile[-1][self.TIME_IDX], 0))

    def __post_init__(self):
        """
        Post initialization method.
        """
        if self.skip_check:
            return

        self._initial_check()
        self._check_dependencies()

        # Check if the velocity profile is valid.
        self._check_velocity_profile()

        # Check if the pressurization time is valid.
        self._check_time_param(self.press_time_ms)
        self._check_time_param(self.depr_time_ms)
        self._add_end_of_procedure()

    def get_time_list(self) -> list[float]:
        """
        Get the time list.
        """
        if self.velocity_profile is None:
            return []

        return [time for time, _ in self.velocity_profile]

    def get_velocity_list(self) -> list[float]:
        """
        Get the velocity list.
        """
        if self.velocity_profile is None:
            return []

        return [velocity for _, velocity in self.velocity_profile]

    def to_csv(self, file_path: str) -> None:
        """Save the procedure parameters to a CSV file.

        Note:
           Delimiter is hardcoded to be a semicolon.

        Args:
            file_path (str): File path
        """
        with open(file_path, "w") as file:
            file.write(f"Procedure name: {self.name}\n")
            file.write(f"Pressurization time: {self.press_time_ms}\n")
            file.write(f"Depressurization time: {self.depr_time_ms}\n\n")

            file.write("time [ms];velocity\n")
            for time, velocity in self.velocity_profile:
                file.write(f"{time};{velocity}\n")

    @staticmethod
    def from_dict(dict: dict[str, Any]) -> Self:
        """Load the procedure parameters from a dictionary.
        The dictionary format:
        {
            "name": str,
            "pressurization": float | None,
            "depressurization": float | None,
            "time_profile": list[float] | None,
            "velocity_profile": list[float] | None,
        }
        Args:
            dict (dict[str, Any]): Dictionary with the procedure parameters

        Returns:
            Self: The procedure parameters
        """
        velocity_profile = dict[ProcedureParameters.KEY_VELOCITY_PROFILE]
        time_profile = dict[ProcedureParameters.KEY_TIME_PROFILE]
        procedure_profile = [
            (time, velocity) for time, velocity in zip(time_profile, velocity_profile)
        ]
        pressurization = dict.get(ProcedureParameters.KEY_PRESS, None)
        depressurization = dict.get(ProcedureParameters.KEY_DEPR, None)

        return ProcedureParameters(
            dict[ProcedureParameters.KEY_NAME],
            procedure_profile,
            pressurization,
            depressurization
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the procedure parameters to a dictionary.
        Returns:
            dict[str, Any]: Dictionary with the procedure parameters
        """
        return {
            self.KEY_NAME: self.name,
            self.KEY_PRESS: self.press_time_ms,
            self.KEY_DEPR: self.depr_time_ms,
            self.KEY_TIME_PROFILE: self.get_time_list(),
            self.KEY_VELOCITY_PROFILE: self.get_velocity_list(),
        }

    def _movement_step_from_tuple(self, step: tuple[float, float]) -> str:
        """Get the movement step from a tuple.

        Args:
            step (tuple[float, float]): Tuple with the step

        Returns:
            str: String with the step
        """
        return f"{int(step[self.TIME_IDX])}:{int(step[self.VELOCITY_IDX])};"

    def procedure_profile_args(self) -> list[str]:
        """Get the procedure profile arguments.
        Returns:
            list[str]: List of arguments
        """
        movement_profile = self._movement_step_from_tuple(self.velocity_profile[0])
        for idx, step in enumerate(self.velocity_profile[1:-1]):
            t_0, v_0 = self.velocity_profile[idx]
            t_1, v_1 = step

            if v_0 != v_1:
                if t_0 == t_1:
                    movement_profile += self._movement_step_from_tuple(step)
                else:
                    for t in np.linspace(t_0, t_1, 6)[1:]:
                        # equation v = v_0 + a * t, where a = (v_1 - v_0) / (t_1 - t_0),
                        # t = (t - t_0)
                        v = v_0 + (v_1 - v_0) * (t - t_0) / (t_1 - t_0)
                        movement_profile += self._movement_step_from_tuple((t, v))

        movement_profile += self._movement_step_from_tuple(self.velocity_profile[-1])
        movement_profile = movement_profile[:-1]

        press_time = self.press_time_ms if self.press_time_ms is not None else 0
        depr_time = self.depr_time_ms if self.press_time_ms is not None else 0

        return [movement_profile, str(press_time), str(depr_time)]
