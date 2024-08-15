import cv2
from datetime import datetime
from src.cameras.handling_elements.basic_handler import BasicHandler


class VideoWriter(BasicHandler):
    def __init__(self, name: str, fps: int, frame_size: tuple[int, int]) -> None:
        self._fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self._writer = None
        self._name = name
        self._fps = fps
        self._frame_size = frame_size

    def _generate_file_name(self) -> str:
        now = datetime.now()
        return f"{self._name}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"


    def start(self) -> None:
        file_name = self._generate_file_name()
        self._writer = cv2.VideoWriter(file_name, self._fourcc, self._fps, self._frame_size, False)

    def stop(self) -> None:
        self._writer.release()
        self._writer = None

    def add_frame(self, frame: list[int]) -> None:
        if self._writer:
            self._writer.write(frame)