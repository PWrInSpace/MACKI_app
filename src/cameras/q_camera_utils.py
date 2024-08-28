from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout
from PySide6.QtCore import Slot
from src.cameras.frame_handlers import FrameDisplay, VideoWriter
from src.cameras.frame_handlers.frame_display import FrameDisplayFormats
from enum import Enum
from dataclasses import dataclass


class CameraStatus(Enum):
    MISSING = "Missing"
    RUNNING = "Running"
    DISPLAYING = "Displaying"
    WRITING = "Writing"
    WRITING_AND_DISPLAYING = "Writing and Displaying"
    DETECTED = "Detected"
    UNKNOWN = "Unknown"


STATUS_TO_COLOR = {
    CameraStatus.MISSING: "red",
    CameraStatus.RUNNING: "yellow",
    CameraStatus.DISPLAYING: "pink",
    CameraStatus.WRITING: "green",
    CameraStatus.WRITING_AND_DISPLAYING: "purple",
    CameraStatus.DETECTED: "cyan",
    CameraStatus.UNKNOWN: "white",
}

DISPLAY_BUTTON_OPEN = "Open"
DISPLAY_BUTTON_CLOSE = "Close"


@dataclass
class CameraDefinition:
    name: str
    id: str


CAMERAS = [
    # CameraDefinition("Front", "DEV_000A471F21DB"),
    CameraDefinition("Ugibugi", "DEV_000F315DEEA8"),
    CameraDefinition("Asdasdasdasdasd", "cam3"),
    CameraDefinition("camera4", "cam4"),
]


class QCamera(QWidget):
    DEFAULT_CONFIG_FILE = None

    DISPLAY_HANDLER = "display"
    WRITER_HANDLER = "writer"

    def __init__(self, name: str, cam_id: str, config_file: str = None) -> None:
        super().__init__()

        self.name = name
        self.id = cam_id
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.handlers = {
            self.DISPLAY_HANDLER: FrameDisplay(self.name, "MACKI_patch.png"),
            self.WRITER_HANDLER: VideoWriter(self.name, 22, (2464, 2056), "videos"),
        }

        self._detected = False
        self._running = False
        self._create_qui_elements()

    ### GUI ###
    def _create_qui_elements(self):
        """Create GUI elements for the camera, this class is not a widget,
        so it contains only the layout elements. It was created like this to
        set this elements on grid in the QCamerasMenager class.
        """
        self.name_label = QLabel(f"{self.name}:")
        self.status_label = QLabel()
        self.update_status()

        self.display_button = QPushButton("Open")
        self.display_button.clicked.connect(self._on_open_button_clicked)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.display_button)

        self.setLayout(self.layout)

    def _on_open_button_clicked(self):
        if self.display_button.text() == DISPLAY_BUTTON_OPEN:
            self.display_button.setText(DISPLAY_BUTTON_CLOSE)
            self.handlers[self.DISPLAY_HANDLER].start()
            self.handlers[self.WRITER_HANDLER].start()
        else:
            self.display_button.setText(DISPLAY_BUTTON_OPEN)
            self.handlers[self.DISPLAY_HANDLER].stop()
            self.handlers[self.WRITER_HANDLER].stop()

        self.update_status()

    def update_status(self):
        status = self.get_str_status()
        self.status_label.setText(status.value)
        self.status_label.setStyleSheet(f"color: {STATUS_TO_COLOR[status]}")

    ### END GUI ###

    def set_detected_flag(self, detected: bool):
        """This method is used to set the detected flag. This class only knows states
        of the handlers, not the camera itself.
        Handlers are connected to cameras and they only receive frames from them.

        Args:
            detected (bool): True if the camera is detected, False otherwise
        """
        self._detected = detected

    @Slot()
    def on_camera_thread_started(self):
        print("Hello")
        self._running = True

    @Slot()
    def on_camera_thread_finished(self):
        self._running = False

    def get_str_status(self) -> str:
        handlers_states = {k: v.is_running for k, v in self.handlers.items()}

        if not self._detected:
            status = CameraStatus.MISSING
        elif (
            handlers_states[self.DISPLAY_HANDLER]
            and handlers_states[self.WRITER_HANDLER]
        ):
            status = CameraStatus.WRITING_AND_DISPLAYING
        elif handlers_states[self.DISPLAY_HANDLER]:
            status = CameraStatus.DISPLAYING
        elif handlers_states[self.WRITER_HANDLER]:
            status = CameraStatus.WRITING
        elif self._running:
            status = CameraStatus.RUNNING
        elif self._detected:
            status = CameraStatus.DETECTED
        else:
            status = CameraStatus.UNKNOWN

        return status
