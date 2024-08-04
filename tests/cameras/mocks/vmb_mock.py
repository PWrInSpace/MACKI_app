from typing import Callable
from vmb_camera_mock import VmbCameraMock
from vmbpy import CameraEvent

class VmbMock:
    class __Instance:
        def __init__(self) -> None:
            # Type to be corrected
            self._camera_change_cb: Callable[[VmbCameraMock, CameraEvent], None] = None
            self._cameras = [
                VmbCameraMock("Camera1"),
                VmbCameraMock("Camera2"),
                VmbCameraMock("Camera3"),
            ]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def get_cameras(self) -> list[VmbCameraMock]:
            return self._cameras

        def register_camera_change_handler(
            self, handler: Callable[[VmbCameraMock, CameraEvent]]
        ) -> None:
            self._camera_change_cb = handler

        def unregister_camera_change_handler(
            self, handler: Callable[[VmbCameraMock, CameraEvent]]
        ) -> None:
            self._camera_change_cb = None

    __instance = __Instance()

    @staticmethod
    def get_instance() -> __Instance:
        """ Get the instance of the VmbMock, with 3 cameras.

        Returns:
            __Instance: The instance of the VmbMock.
        """
        return VmbMock.__instance

