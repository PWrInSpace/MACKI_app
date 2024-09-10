import cv2
from enum import Enum
from PySide6.QtGui import QImage


class FrameDisplayFormats(Enum):
    GRAY = QImage.Format.Format_Grayscale8
    RGB = QImage.Format.Format_RGB888

    def to_cv2_format(self) -> int:
        match self:
            case FrameDisplayFormats.GRAY:
                return cv2.IMREAD_GRAYSCALE
            case FrameDisplayFormats.RGB:
                return cv2.IMREAD_COLOR
            case _:
                raise ValueError("Invalid format")
