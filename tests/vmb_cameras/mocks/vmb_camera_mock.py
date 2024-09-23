from typing import Callable
import numpy as np


class VmbCameraMock:
    def __init__(self, camera_id: str) -> None:
        self._camera_id = camera_id

    def get_id(self) -> str:
        return self._camera_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def start_streaming(self, on_frame: Callable[[np.ndarray], None]) -> None:
        pass

    def stop_streaming(self) -> None:
        pass
