import cv2
import os
import uuid
import numpy.typing as npt
from datetime import datetime
from typing import override
from src.cameras.frame_handlers.basic_frame_handler import BasicFrameHandler, logger
from PySide6.QtCore import QMutex


class VideoWriter(BasicFrameHandler):
    LOCK_TIMEOUT = 1000

    def __init__(
        self, name: str, fps: int, frame_size: tuple[int, int], out_folder: str = None
    ) -> None:
        """Create a video writer to save frames to a video file.

        Args:
            name (str): The name of the video file.
            fps (int): The frames per second of the video.
            frame_size (tuple[int, int]): The size of the frames.
        """
        self._fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self._writer = None
        self._name = name
        self._fps = fps
        self._frame_size = frame_size
        self._out_folder = out_folder
        self._writer_mutex = QMutex()

        self._check_out_folder()
        super().__init__()

    def __del__(self) -> None:
        """Destructor, release the video writer if it's still running"""
        if self._writer:
            self._writer.release()

    def _check_out_folder(self) -> None:
        """Check if the output folder exists, if not create it."""
        if self._out_folder:
            if not os.path.exists(self._out_folder):
                os.makedirs(self._out_folder)

    def _generate_file_path(self) -> str:
        """Generate a file name for the video file.
            str: The generated file name in the format: "<name>_<current_date_time>.mp4"

        Returns:
            str: _description_
        """
        now = datetime.now()
        name = f"{self._name}_{now.strftime('%Y-%m-%d_%H-%M-%S.%f')}.mp4"

        if self._out_folder:
            path = os.path.join(self._out_folder, name)
        else:
            path = name

        if os.path.isfile(path):
            without_extension = os.path.splitext(".")[0]
            random_string = str(uuid.uuid4())
            path = f"{without_extension}_{random_string}.mp4"

        return path

    @override
    def start(self) -> None:
        """Start the video writer, this method creates a new video"""
        file_name = self._generate_file_path()

        if self._writer_mutex.tryLock(1000) is False:
            logger.error("Unable to lock writer mutex")
            return

        self._writer = cv2.VideoWriter(
            file_name, self._fourcc, self._fps, self._frame_size, True
        )
        self._writer_mutex.unlock()

        logger.info(f"Starting video writer for {self._name}, file: {file_name}")
        super().start()

    @override
    def stop(self) -> None:
        """Stop the video writer, this method release the video writer"""
        if not self.is_running:
            logger.warning("Video writer is not running")
            return

        logger.info(f"Stopping video writer for {self._name}")
        if self._writer_mutex.tryLock(self.LOCK_TIMEOUT) is False:
            return

        self._writer.release()
        self._writer = None
        self._writer_mutex.unlock()

        super().stop()

    @override
    def add_frame(self, frame: npt.ArrayLike) -> None:
        """Add a frame to the video writer.

        Args:
            frame (npt.ArrayLike): The frame to be added to the video.
        """
        if not self._writer:
            return

        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        if (frame_width != self._frame_size[0]) or (
            frame_height != self._frame_size[1]
        ):
            self.stop()
            raise RuntimeError(
                f"Frame size ({frame.shape[1]}, {frame.shape[0]})"
                f"does not match video frame size {self._frame_size}"
            )

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if self._writer_mutex.tryLock(self.LOCK_TIMEOUT):
            try:
                if self._writer:
                    self._writer.write(frame)
            except Exception:
                logger.error("Exception in writer write")
            finally:
                self._writer_mutex.unlock()

    @override
    @property
    def is_running(self) -> bool:
        """Check if the video writer is running."""
        return self._writer is not None

    def change_output_dir(self, out_dir_path: str) -> bool:
        """Change the output directory of the video writer.

        Args:
            out_dir_paht (str): The new output directory path.

        Returns:
            bool: True if the output directory was changed successfully, False otherwise.
        """
        if self.is_running:
            return False

        self._out_folder = out_dir_path
        self._check_out_folder()

        return True
