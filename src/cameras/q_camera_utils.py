from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtCore import QObject
from src.cameras.frame_handlers import FrameDisplay, VideoWriter
from dataclasses import dataclass
from enum import Enum

class CameraStatus(Enum):
    MISSING = "Missing"
    RUNNING = "Running"
    DISPLAYING = "Displaying"
    WRITING = "Writing"
    WRITING_AND_DISPLAYING = "Writing and Displaying"

STATUS_TO_COLOR = {
    CameraStatus.MISSING: "red",
    CameraStatus.RUNNING: "yellow",
    CameraStatus.DISPLAYING: "blue",
    CameraStatus.WRITING: "green",
    CameraStatus.WRITING_AND_DISPLAYING: "purple"
}

@dataclass
class CameraDefinition:
    name: str
    id: str

CAMERAS = [
    CameraDefinition("camera1", "cam1"),
    CameraDefinition("camera2", "cam2"),
    CameraDefinition("camera3", "cam3"),
    CameraDefinition("camera4", "cam4"),
]

class QCamera:
    DEFAULT_CONFIG_FILE = "default_confg.txt"

    DISPLAY_HANDLER = "display"
    WRITER_HANDLER = "writer"

    def __init__(self, name: str, cam_id: str, config_file: str = None) -> None:
        self.name = name
        self.id = cam_id
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.handlers = {
            self.DISPLAY_HANDLER: FrameDisplay(self.name),
            self.WRITER_HANDLER: VideoWriter(self.name, 10, (640, 480))
        }

        self._running = False
        self._create_qui_elements()

### GUI ###
    def _create_qui_elements(self):
        """ Create GUI elements for the camera, this class is not a widget,
        so it contains only the layout elements. It was created like this to
        set this elements on grid in the QCamerasMenager class.
        """
        self._name_label = QLabel(f"{self.name}:")
        self._status_label = QLabel()
        self.update_status()

        self._display_button = QPushButton("Open")
        self._display_button.clicked.connect(self._on_open_button_clicked)

    def _on_open_button_clicked(self):
        self.handlers[self.DISPLAY_HANDLER].start()

    def get_name_label(self) -> QLabel:
        return self._name_label

    def get_status_label(self) -> QLabel:
        return self._status_label

    def get_display_button(self) -> QPushButton:
        return self._display_button

    def update_status(self):
        status = self.get_str_status()
        self._status_label.setText(status.value)
        self._status_label.setStyleSheet(f"background-color: {STATUS_TO_COLOR[status]}")
### END GUI ###

    def set_running_flag(self, running: bool):
        """ This method is used to set the running flag. This class only knows states
        of the handlers, not the camera itself.
        Handlers are connected to cameras and they only receive frames from them.

        Args:
            running (bool): True if the camera is running, False otherwise
        """
        self._running = running


    def get_str_status(self) -> str:
        handlers_states = {k: v.is_running() for k, v in self.handlers.items()}

        if handlers_states[self.DISPLAY_HANDLER] and handlers_states[self.WRITER_HANDLER]:
            status = CameraStatus.WRITING_AND_DISPLAYING
        elif handlers_states[self.DISPLAY_HANDLER]:
            status =  CameraStatus.DISPLAYING
        elif handlers_states[self.WRITER_HANDLER]:
            status = CameraStatus.WRITING
        elif not self._running:
            status =  CameraStatus.MISSING
        else:
            status =  CameraStatus.RUNNING

        return status
