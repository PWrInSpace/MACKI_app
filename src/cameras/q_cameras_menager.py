from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer
from src.cameras.cameras_menager import CamerasMenager
from src.cameras.camera_handler import CameraHandler, logger
from src.cameras.q_camera_utils import (
    QCamera,
    CAMERAS,
    STATUS_TO_COLOR
)


class QCamerasMenager(QWidget):
    STATUS_UPDATE_INTERVAL_MS = 100
    def __init__(self) -> None:
        super().__init__()

        self._cameras_menager = CamerasMenager()
        self._cameras_menager.camera_registered.connect(self._on_camera_registered)
        self._cameras_menager.camera_missing.connect(self._on_camera_missing)
        self._cameras_configs = {cam.id: QCamera(cam.name, cam.id) for cam in CAMERAS}
        self._init_ui()

        self._status_update_timer = QTimer()
        self._status_update_timer.timeout.connect(self._update_cameras_status)
        self._status_update_timer.start(self.STATUS_UPDATE_INTERVAL_MS)

    def _init_ui(self) -> None:
        layout = QVBoxLayout()

        for i, camera in enumerate(self._cameras_configs.values()):
            layout.addWidget(camera)

        self.setLayout(layout)

    def _on_camera_registered(self, camera: CameraHandler) -> None:
        id = camera.get_id()

        if id not in self._cameras_configs:
            logger.error(f"Unknown camera id {id}")
            return

        for handler in self._cameras_configs[id].handlers.values():
            camera.register_handler(handler)

        camera.set_config_file(self._cameras_configs[id].config_file)
        camera.start()

        self._cameras_configs[id].set_running_flag(True)

    def _on_camera_missing(self, camera_id: str) -> None:
        logger.warning(f"Camera {camera_id} missing")
        self._cameras_configs[camera_id].set_running_flag(False)

    def _update_cameras_status(self) -> None:
        for camera in self._cameras_configs.values():
            camera.update_status()

    def enable_cameras(self):
        self._cameras_menager.start()