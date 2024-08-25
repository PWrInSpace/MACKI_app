from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox, QPushButton
from src.cameras.cameras_menager import CamerasMenager
from src.cameras.camera_handler import CameraHandler, logger
from src.cameras.q_camera_utils import (
    QCamera,
    CAMERAS,
    STATUS_TO_COLOR
)


class QCamerasMenager(QWidget):
    GUI_NAME_IDX = 0
    GUI_STATUS_IDX = 1
    GUI_BUTTON_IDX = 2

    def __init__(self) -> None:
        super().__init__()

        self._cameras_menager = CamerasMenager()
        self._cameras_menager.camera_registered.connect(self._on_camera_registered)
        self._cameras_menager.camera_missing.connect(self._on_camera_missing)

        self._cameras_configs = {cam.id: QCamera(cam.name, cam.id) for cam in CAMERAS}
        self._cameras_gui = {}

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QGridLayout()

        for i, camera_config in enumerate(self._cameras_configs.values()):
            name_label = QLabel(camera_config.name)
            status_label = QLabel()
            button = QPushButton("Open")

            layout.addWidget(name_label, i, 0)
            layout.addWidget(status_label, i, 1)
            layout.addWidget(button, i, 2)

            self._cameras_gui[camera_config.id] = (name_label, status_label, button)

            self._update_status(camera_config.id)

        self.setLayout(layout)

    def _update_status(self, camera_id: str) -> None:
        status = self._cameras_configs[camera_id].get_str_status()
        status_label = self._cameras_gui[camera_id][self.GUI_STATUS_IDX]

        status_label.setText(status.value)
        status_label.setStyleSheet(f"color: {STATUS_TO_COLOR[status]}")

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

    def enable_cameras(self):
        self._cameras_menager.start()