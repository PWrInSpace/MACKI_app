import os
from src.app.camera_widget import QCameraWidget
from src.cameras.q_cameras_menager import QCamerasManager
from src.cameras.frame_handlers import FrameDisplay, VideoWriter
from src.cameras.frame_handlers import FrameDisplayFormats

# TEMPORARY
MAKO_CONFIG_FILE = os.path.join("config", "mako.xml")
ALVIUM_CONFIG_FILE = os.path.join("config", "alvium2.xml")

# MAKO_CONFIG_FILE = None
# ALVIUM_CONFIG_FILE = None

MACKI_LOGO_PATH = os.path.join("resources", "MACKI_patch.png")
DEFAULT_FRAME_SIZE = (500, 500)
MINI_FRAME_SIZE = (300, 300)
FRAME_FORMAT = FrameDisplayFormats.GRAY

VIDEO_FPS = 11
VIDEO_RESOLUTION = (1936, 1216)
VIDEO_DIR = "videos"


class QCameraApp(QCamerasManager):
    """
    Camera app - main widget, handling all cameras and
    widgets for displaying and writing frames.
    """
    OCTOPUS_LOGO = os.path.join(os.getcwd(), "resources", "octopus_apple.png")

    def __init__(self):
        cameras = [
            QCameraWidget(
                name="CAM1",
                id="DEV_000F315DEEA8",
                handlers=[
                    FrameDisplay(
                        "CAM1",
                        MACKI_LOGO_PATH,
                        DEFAULT_FRAME_SIZE,
                        MINI_FRAME_SIZE,
                        FRAME_FORMAT,
                        self.OCTOPUS_LOGO
                    ),
                    VideoWriter("CAM1", VIDEO_FPS, VIDEO_RESOLUTION, VIDEO_DIR),
                ],
                camera_config_file=MAKO_CONFIG_FILE,
            ),
            QCameraWidget(
                name="CAM2",
                id="DEV_000F315DEEAA",
                handlers=[
                    FrameDisplay(
                        "CAM2",
                        MACKI_LOGO_PATH,
                        DEFAULT_FRAME_SIZE,
                        MINI_FRAME_SIZE,
                        FRAME_FORMAT,
                        self.OCTOPUS_LOGO
                    ),
                    VideoWriter("CAM2", VIDEO_FPS, VIDEO_RESOLUTION, VIDEO_DIR),
                ],
                camera_config_file=MAKO_CONFIG_FILE,
            ),
            QCameraWidget(
                name="CAM3",
                id="DEV_000F315DF005",
                handlers=[
                    FrameDisplay(
                        "CAM3",
                        MACKI_LOGO_PATH,
                        DEFAULT_FRAME_SIZE,
                        MINI_FRAME_SIZE,
                        FRAME_FORMAT,
                        self.OCTOPUS_LOGO
                    ),
                    VideoWriter("CAM3", VIDEO_FPS, VIDEO_RESOLUTION, VIDEO_DIR),
                ],
                camera_config_file=MAKO_CONFIG_FILE,
            ),
            QCameraWidget(
                name="Alvium",
                id="DEV_000A471F21DB",
                handlers=[
                    FrameDisplay(
                        "Alvium",
                        MACKI_LOGO_PATH,
                        DEFAULT_FRAME_SIZE,
                        MINI_FRAME_SIZE,
                        FRAME_FORMAT,
                        self.OCTOPUS_LOGO
                    ),
                    VideoWriter("Alvium", 9, (1216, 1936), VIDEO_DIR),
                ],
                camera_config_file=ALVIUM_CONFIG_FILE,
            ),
        ]

        super().__init__(cameras)
