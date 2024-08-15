import numpy as np
import cv2
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from src.cameras.handling_elements.basic_handler import BasicHandler, logger


class FrameDisplay(BasicHandler):
    def __init__(self, name) -> None:
        self.widget = QWidget()
        self.widget.setWindowTitle(name)

        self._label = QLabel("Frame display")
        layout = QVBoxLayout()
        layout.addWidget(self._label)
        # self.widget.setFixedSize(640, 480)
        self.widget.setLayout(layout)

    def generate_init_frame(self) -> np.array:
        dark_img = np.zeros((480, 640, 3))

        text = "Waiting for image"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 3
        font_thickness = 10
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        text_x = (dark_img.shape[1] - text_size[0]) // 2
        text_y = (dark_img.shape[0] + text_size[1]) // 2
        img = cv2.putText(dark_img, text, (200, 200), font, font_scale, (255, 0, 0), font_thickness)
        return img

    def start(self) -> None:
        logger.info(f"Starting frame display for {self.widget.windowTitle()}")
        self.widget.show()
        self.add_frame(self.generate_init_frame())

    def stop(self) -> None:
        logger.info(f"Stopping frame display for {self.widget.windowTitle()}")
        self.widget.close()

    def add_frame(self, frame: np.ndarray) -> None:
        if self.widget.isVisible():
            img = QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
            pix = QPixmap(img)
            self._label.setPixmap(pix)