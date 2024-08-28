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
class CameraConfig:
    name: str
    id: str
    handlers: str
    camera_config_file: str = None
