import logging
from typing import Self, Any
from dataclasses import dataclass

logger = logging.getLogger("procedure_parameters")


@dataclass
class ProcedureParameters:
    """
    Data class for procedure parameters.
    """
    MAX_VELOCITY = 100_000
    MIN_VELOCITY = -100_000
    TIME_IDX = 0
    VELOCITY_IDX = 1

    # The name of the procedure.
    name: str
    # The velocity profile of the procedure., list of tuples (time, velocity)
    velocity_profile: list[tuple[float, float]] | None
    # The time of pressurization of the system.
    pressurization_time_ms: float | None
    # The time of depressurization of the system.
    depressurization_time_ms: float | None
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

        if self.pressurization_time_ms is not None and\
           not isinstance(self.pressurization_time_ms, (int, float)):
            raise ValueError("The pressurization time is not a number.")

        if self.depressurization_time_ms is not None and\
           not isinstance(self.depressurization_time_ms, (int, float)):
            raise ValueError("The depressurization time is not a number.")

        if self.velocity_profile is None and\
           (self.pressurization_time_ms is None or self.depressurization_time_ms is None):
            raise ValueError(
                "The velocity profile is None and the press or depress time is None."
            )

        if self.pressurization_time_ms is not None and self.depressurization_time_ms is None:
            raise ValueError("The pressurization time is set but not the depressurization.")

        if self.pressurization_time_ms is None and self.depressurization_time_ms is not None:
            raise ValueError("The depressurization time is set but not the pressurization.")

        if self.pressurization_time_ms is not None and self.depressurization_time_ms is not None:
            if self.pressurization_time_ms < 0 or self.depressurization_time_ms < 0:
                raise ValueError("Pressurization or depressurization time is negative.")

        if self.pressurization_time_ms is not None and self.depressurization_time_ms is not None:
            if self.pressurization_time_ms > self.depressurization_time_ms:
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

        if self.velocity_profile[0][self.TIME_IDX] != 0:
            raise ValueError("The first time value is not 0.")

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

    def __post_init__(self):
        """
        Post initialization method.
        """
        if self.skip_check:
            return

        self._initial_check()

        # Check if the velocity profile is valid.
        self._check_velocity_profile()

        # Check if the pressurization time is valid.
        self._check_time_param(self.pressurization_time_ms)
        self._check_time_param(self.depressurization_time_ms)

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
            file.write(f"Pressurization time: {self.pressurization_time_ms}\n")
            file.write(f"Depressurization time: {self.depressurization_time_ms}\n\n")

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
        velocity_profile = dict["velocity_profile"]
        time_profile = dict["time_profile"]
        procedure_profile = [
            (time, velocity) for time, velocity in zip(time_profile, velocity_profile)
        ]

        return ProcedureParameters(
            dict["name"],
            procedure_profile,
            dict["pressurization"],
            dict["depressurization"],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the procedure parameters to a dictionary.
        Returns:
            dict[str, Any]: Dictionary with the procedure parameters
        """
        return {
            "name": self.name,
            "pressurization": self.pressurization_time_ms,
            "depressurization": self.depressurization_time_ms,
            "time_profile": self.get_time_list(),
            "velocity_profile": self.get_velocity_list(),
        }
