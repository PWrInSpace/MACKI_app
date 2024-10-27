from src.app.cameras.camera_widget import QCameraWidget
from src.cameras.q_cameras_menager import QCamerasManager
from src.cameras.frame_handlers import FrameDisplay, VideoWriter
from src.app.config import (
    OCTOPUS_CAM_WIN,
    MACKI_LOGO_PATH,
    DEFAULT_FRAME_SIZE,
    MINI_FRAME_SIZE,
    FRAME_FORMAT,
    VIDEO_FPS,
    VIDEO_RESOLUTION,
    VIDEO_DIR,
    CAMERA_CONFIG,
)


class QCameraApp(QCamerasManager):
    """
    Camera app - main widget, handling all cameras and
    widgets for displaying and writing frames.
    """

    CAMERAS = {
        "CAM1": "DEV_000A4727B2BF",
        "CAM2": "DEV_000A472B9D47",
        "CAM3": "DEV_000A4722822F",
        "CAM4": "DEV_000A4715D9F0",
    }

    def __init__(self):
        self._video_writers = []
        self._frame_displays = []
        self._cameras = []

        for name, camera_id in self.CAMERAS.items():
            self._create_camera_widget(name, camera_id)

        super().__init__(self._cameras)

    def _create_camera_widget(self, name: str, camera_id: str) -> None:
        video_writer = VideoWriter(name, VIDEO_FPS, VIDEO_RESOLUTION, VIDEO_DIR)
        frame_display = FrameDisplay(
            name,
            MACKI_LOGO_PATH,
            DEFAULT_FRAME_SIZE,
            MINI_FRAME_SIZE,
            FRAME_FORMAT,
            OCTOPUS_CAM_WIN,
        )
        camera = QCameraWidget(
            name, camera_id, [frame_display, video_writer], CAMERA_CONFIG
        )

        self._video_writers.append(video_writer)
        self._frame_displays.append(frame_display)
        self._cameras.append(camera)

    def change_output_dir(self, new_dir: str) -> None:
        for writer in self._video_writers:
            if not writer.change_output_dir(new_dir):
                raise RuntimeError(f"Failed to change output dir for {writer.name}")

    def start_video_recording(self) -> None:
        for writer, camera in zip(self._video_writers, self._cameras):
            if camera.initialized:
                writer.start()

    def stop_video_recording(self) -> None:
        for writer in self._video_writers:
            writer.stop()
