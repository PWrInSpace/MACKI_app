import numpy as np
import cv2
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from src.cameras.frame_handlers.basic_handler import BasicHandler, logger


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
        logger.info(f"Starting frame display for {self.widget.windowTitle()}")
        self.widget.show()
        self.add_frame(self.generate_init_frame())

    def stop(self) -> None:
        logger.info(f"Stopping frame display for {self.widget.windowTitle()}")
        self.widget.close()

    def add_frame(self, frame: np.ndarray) -> None:
        if self.is_running():
            # logger.debug(f"Adding frame to {self.widget.windowTitle()}")
            fr = cv2.resize(frame, (640, 480))
            logger.info(f"Adding frame {fr.shape}")
            img = QImage(fr, fr.shape[1], fr.shape[0], QImage.Format_Grayscale8)
            pix = QPixmap(img)
            self._label.setPixmap(pix)

    def is_running(self) -> bool:
        return self.widget.isVisible()