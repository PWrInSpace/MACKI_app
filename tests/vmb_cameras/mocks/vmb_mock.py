from typing import Callable
from tests.vmb_cameras.mocks.vmb_camera_mock import VmbCameraMock
from vmbpy import CameraEvent


class VmbInstance:
    CAM1_ID = "Camera1"
    CAM2_ID = "Camera2"
    CAM3_ID = "Camera3"

    def __init__(self) -> None:
        # Type to be corrected
        self._camera_change_cb: Callable[[VmbCameraMock, CameraEvent], None] = None
        self._cameras = [
            VmbCameraMock(self.CAM1_ID),
            VmbCameraMock(self.CAM2_ID),
            VmbCameraMock(self.CAM3_ID),
        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def get_all_cameras(self) -> list[VmbCameraMock]:
        return self._cameras

    def register_camera_change_handler(
        self, handler: Callable[[VmbCameraMock, CameraEvent], None]
    ) -> None:
        self._camera_change_cb = handler

    def unregister_camera_change_handler(
        self, handler: Callable[[VmbCameraMock, CameraEvent], None]
    ) -> None:
        self._camera_change_cb = None

    def emit_camera_change(self, camera: VmbCameraMock, event: CameraEvent) -> None:
        if self._camera_change_cb:
            self._camera_change_cb(camera, event)
