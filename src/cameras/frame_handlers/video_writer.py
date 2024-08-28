import cv2
import os
from datetime import datetime
from typing import override
from src.cameras.frame_handlers.basic_handler import BasicHandler, logger


class VideoWriter(BasicHandler):
    def __init__(
            self,
            name: str,
            fps: int,
            frame_size: tuple[int, int],
            out_folder: str = None
        ) -> None:
        """ Create a video writer to save frames to a video file.

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

        self._check_out_folder()
        super().__init__()

    def __del__(self) -> None:
        """ Destructor, release the video writer if it's still running
        """
        if self._writer:
            self._writer.release()

    def _check_out_folder(self) -> None:
        """ Check if the output folder exists, if not create it.
        """
        if self._out_folder:
            if not os.path.exists(self._out_folder):
                os.makedirs(self._out_folder)

    def _generate_file_path(self) -> str:
        """ Generate a file name for the video file.
            str: The generated file name in the format: "<name>_<current_date_time>.mp4"

        Returns:
            str: _description_
        """
        now = datetime.now()
        name = f"{self._name}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"

        if self._out_folder:
            path = os.path.join(self._out_folder, name)
        else:
            path = name

        return path

    @override
    def start(self) -> None:
        """ Start the video writer, this method creates a new video """
        file_name = self._generate_file_path()
        self._writer = cv2.VideoWriter(
            file_name, self._fourcc, self._fps, self._frame_size, False
        )
        super().start()

    @override
    def stop(self) -> None:
        """ Stop the video writer, this method release the video writer """
        if not self.is_running:
            logger.warning("Video writer is not running")
            return
        
        self._writer.release()
        self._writer = None
        super().stop()

    @override
    def add_frame(self, frame: list[int]) -> None:
        """ Add a frame to the video writer.

        Args:
            frame (list[int]): The frame to be added to the video.
        """
        if self._writer:
            self._writer.write(frame)

    @override
    @property
    def is_running(self) -> bool:
        """ Check if the video writer is running. """
        return self._writer is not None
