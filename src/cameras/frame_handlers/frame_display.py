import numpy as np
import cv2
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from src.cameras.frame_handlers.basic_handler import BasicHandler, logger
from src.cameras.frame_handlers.display_window import ImageDisplayWindow


class FrameDisplay(BasicHandler):
    def __init__(self, name) -> None:
        self.window = ImageDisplayWindow(name)
        self.window.close_event.connect(self.stop)
        super().__init__()

    def generate_init_frame(self) -> np.array:
        dark_img = np.zeros((480, 640))

        text = "Waiting for image"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 3
        font_thickness = 10
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        text_x = (dark_img.shape[1] - text_size[0]) // 2
        text_y = (dark_img.shape[0] + text_size[1]) // 2
        img = cv2.putText(dark_img, text, (200, 200), font, font_scale, 255, font_thickness)
        cv2.imwrite("dark_img.jpg", img)
        return img

    def start(self) -> None:
        logger.info(f"Starting frame display for {self.window.windowTitle()}")
        if not self.is_running:
            self.window.show()
            self.window.update_image(self.generate_init_frame())
            super().start()

    def stop(self) -> None:
        logger.info(f"Stopping frame display for {self.window.windowTitle()}")
        self.window.close()
        super().stop()

    def add_frame(self, frame: np.ndarray) -> None:
        if self.is_running:
            self.window.update_image(frame)

    @property
    def is_running(self) -> bool:
        return self.window.isVisible()