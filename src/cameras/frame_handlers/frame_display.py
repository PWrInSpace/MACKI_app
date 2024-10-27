import os
import cv2
import numpy as np
import numpy.typing as npt
from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QIcon

from src.cameras.frame_handlers.basic_frame_handler import BasicFrameHandler, logger
from src.utils.qt.image_display_window import ImageDisplayWindow

from src.cameras.frame_handlers.frame_display_utils import FrameDisplayFormats


class FrameDisplay(BasicFrameHandler):
    def __init__(
        self,
        name,
        default_image_path: str = "",
        default_frame_size: tuple[int, int] = (600, 600),
        minimum_frame_size: tuple[int, int] = (200, 200),
        image_format: FrameDisplayFormats = FrameDisplayFormats.GRAY,
        icon_path: str = "",
    ) -> None:
        self.window = ImageDisplayWindow(
            name, default_frame_size, minimum_frame_size, image_format.value
        )
        self.window.close_event.connect(self.stop)

        self._image_format = image_format
        self._default_image_path = default_image_path

        if icon_path:
            self.window.setWindowIcon(QIcon(icon_path))

        super().__init__()

    def generate_init_frame(self) -> npt.ArrayLike:
        """Generate an initial frame to be displayed when the handler starts

        Returns:
            npt.ArrayLike: The initial frame
        """
        if os.path.isfile(self._default_image_path):
            cv2_format = self._image_format.to_cv2_format()
            img = cv2.imread(self._default_image_path, cv2_format)

            # Convert the image to from BGR to RGB if the format is RGB
            if cv2_format == cv2.IMREAD_COLOR:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img = np.zeros((600, 600), np.uint8)

        return img

    @override
    def start(self) -> None:
        """Start the handler, this method emit the started signal and show the window"""
        logger.info(f"Starting frame display for {self.window.windowTitle()}")
        if not self.is_running:
            self.window.show()
            self.window.update_image(self.generate_init_frame())
            super().start()

    @override
    @Slot()
    def stop(self) -> None:
        """Stop the handler, this method emit the stopped signal and close the window"""
        logger.info(f"Stopping frame display for {self.window.windowTitle()}")
        self.window.hide()
        logger.info(f"Frame display for {self.window.windowTitle()} stopped")
        super().stop()

    @override
    def add_frame(self, frame: np.ndarray) -> None:
        """Add a frame to the handler and update the window image if it is open"""
        if self.is_running:
            self.window.update_image(frame)

    @override
    @property
    def is_running(self) -> bool:
        """Check if the handler is running"""
        return self.window.isVisible()

    @override
    @property
    def close_event(self) -> Signal:
        """Get the close event signal

        Returns:
            Signal: The close event signal
        """
        return self.window.close_event
