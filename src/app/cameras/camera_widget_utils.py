from enum import Enum
from dataclasses import dataclass


class CameraStatus(Enum):
    """QCameraWidget status"""

    MISSING = "Missing"
    RUNNING = "Running"
    DISPLAYING = "Displaying"
    WRITING = "Writing"
    WRITING_AND_DISPLAYING = "Writing and Displaying"
    DETECTED = "Detected"
    UNKNOWN = "Unknown"


STATUS_TO_COLOR = {
    CameraStatus.MISSING: "#FF204E",
    CameraStatus.RUNNING: "#A3D8FF",
    CameraStatus.DISPLAYING: "#15F5BA",
    CameraStatus.WRITING: "#AF47D2",
    CameraStatus.WRITING_AND_DISPLAYING: "#B8B5FF",
    CameraStatus.DETECTED: "#9BEC00",
    CameraStatus.UNKNOWN: "#F6FA70",
}


@dataclass
class CameraConfig:
    """Camera configuration dataclass"""

    name: str
    id: str
    handlers: str
    camera_config_file: str = None
