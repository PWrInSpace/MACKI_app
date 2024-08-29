from src.app.camera_widget import QCameraWidget
from src.cameras.q_cameras_menager import QCamerasMenager
from src.cameras.frame_handlers import FrameDisplay, VideoWriter
from src.cameras.frame_handlers import FrameDisplayFormats

# TEMPORARY
ALVIUM_CONFIG_FILE = "mako.xml"

MACKI_LOGO_PATH = "MACKI_patch.png"
DEFAULT_FRAME_SIZE = (500, 500)
MINI_FRAME_SIZE = (300, 300)
FRAME_FORMAT = FrameDisplayFormats.GRAY

VIDEO_FPS = 10
VIDE_RESOLUTION = (1936, 1216)
VIDEO_DIR = "videos"


class QCameraApp(QCamerasMenager):
    """
    Camera app - main widget, handling all cameras and
    widgets for displaying and writing frames.
    """
    def __init__(self):
        cameras = [
            QCameraWidget(
                name="Ugibugi",
                id="DEV_000F315DEEA8",
                handlers=[
                    FrameDisplay(
                        "Ugibugi",
                        MACKI_LOGO_PATH,
                        DEFAULT_FRAME_SIZE,
                        MINI_FRAME_SIZE,
                        FRAME_FORMAT,
                    ),
                    VideoWriter("Ugibugi", VIDEO_FPS, VIDE_RESOLUTION, VIDEO_DIR),
                ],
                camera_config_file=ALVIUM_CONFIG_FILE,
            ),
            QCameraWidget(
                name="Camera 2",
                id="2",
                handlers=[
                    FrameDisplay(
                        "Camera 2",
                        MACKI_LOGO_PATH,
                        DEFAULT_FRAME_SIZE,
                        MINI_FRAME_SIZE,
                        FRAME_FORMAT,
                    ),
                    VideoWriter("Camera 2", VIDEO_FPS, VIDE_RESOLUTION, VIDEO_DIR),
                ],
                camera_config_file=ALVIUM_CONFIG_FILE,
            ),
        ]

        super().__init__(cameras)
