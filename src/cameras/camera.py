from vmbpy import Camera
from PySide6.QtCore import QThread

class CameraHandler:
    def __init__(self, camera: Camera) -> None:
        self._camera = camera

    def run(self) -> None:
        pass

    @property
    def camera_id(self) -> str:
        return self._camera.get_id()