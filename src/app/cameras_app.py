import os
from src.app.camera_widget import QCameraWidget
from src.cameras.q_cameras_menager import QCamerasManager
from src.cameras.frame_handlers import FrameDisplay, VideoWriter
from src.cameras.frame_handlers import FrameDisplayFormats

# TEMPORARY
MAKO_CONFIG_FILE = os.path.join("config", "mako.xml")
ALVIUM_CONFIG_FILE = os.path.join("config", "alvium2.xml")
TEST_CONFIG_FILE = os.path.join("config", "DEV_000A4727B2BF_settings.xml")
# MAKO_CONFIG_FILE = None
# ALVIUM_CONFIG_FILE = None

MACKI_LOGO_PATH = os.path.join("resources", "MACKI_patch.png")
DEFAULT_FRAME_SIZE = (500, 500)
MINI_FRAME_SIZE = (300, 300)
FRAME_FORMAT = FrameDisplayFormats.RGB

VIDEO_FPS = 10
VIDEO_RESOLUTION = (1936, 1216)
VIDEO_DIR = "videos"


class QCameraApp(QCamerasManager):
    """
    Camera app - main widget, handling all cameras and
    widgets for displaying and writing frames.
    """

    def __init__(self, frame_display_icon_path: str = ""):
        cameras = [
            QCameraWidget(
                name="CAM1",
                id="DEV_000A4727B2BF",
                handlers=[
                    FrameDisplay(
                        "CAM1",
                        MACKI_LOGO_PATH,
                        DEFAULT_FRAME_SIZE,
                        MINI_FRAME_SIZE,
                        FRAME_FORMAT,
                        frame_display_icon_path,
                    ),
                    VideoWriter("CAM1", VIDEO_FPS, VIDEO_RESOLUTION, VIDEO_DIR),
                ],
                camera_config_file=TEST_CONFIG_FILE,
            ),
            QCameraWidget(
                name="CAM2",
                id="DEV_000A472B9D47",
                handlers=[
                    FrameDisplay(
                        "CAM2",
                        MACKI_LOGO_PATH,
                        DEFAULT_FRAME_SIZE,
                        MINI_FRAME_SIZE,
                        FRAME_FORMAT,
                        frame_display_icon_path,
                    ),
                    VideoWriter("CAM2", VIDEO_FPS, VIDEO_RESOLUTION, VIDEO_DIR),
                ],
                camera_config_file=TEST_CONFIG_FILE,
            ),
            QCameraWidget(
                name="CAM3",
                id="DEV_000A4722822F",
                handlers=[
                    FrameDisplay(
                        "CAM3",
                        MACKI_LOGO_PATH,
                        DEFAULT_FRAME_SIZE,
                        MINI_FRAME_SIZE,
                        FRAME_FORMAT,
                        frame_display_icon_path,
                    ),
                    VideoWriter("CAM3", VIDEO_FPS, VIDEO_RESOLUTION, VIDEO_DIR),
                ],
                camera_config_file=TEST_CONFIG_FILE,
            ),
            QCameraWidget(
                name="CAM4",
                id="DEV_000A4715D9F0",
                handlers=[
                    FrameDisplay(
                        "CAM4",
                        MACKI_LOGO_PATH,
                        DEFAULT_FRAME_SIZE,
                        MINI_FRAME_SIZE,
                        FRAME_FORMAT,
                        frame_display_icon_path,
                    ),
                    VideoWriter("CAM4", 9, VIDEO_RESOLUTION, VIDEO_DIR),
                ],
                camera_config_file=TEST_CONFIG_FILE,
            ),
        ]

        super().__init__(cameras)
