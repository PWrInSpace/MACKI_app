import cv2
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class ImageDisplayWindow(QLabel):
    def __init__(self, name) -> None:
        super().__init__()
        self.setWindowTitle(name)

        self._minimum_size = (400, 400)

        self.setScaledContents(True)

        window_size = self.size()
        print(window_size)
        self._display_size = (window_size.width() - 20, window_size.height() - 20)
        self.setMinimumSize(self._minimum_size[0], self._minimum_size[1])

        self._image = None

    def resizeEvent(self, resize_event) -> None:
        size = resize_event.size()
        old_size = resize_event.oldSize()
        if size.width() < 400 or size.height() < 400:
            return
        
        # if size.width() == old_size.width() or size.height() == old_size.height():
        #     self._display_size = (size.width() - 5, size.height() - 5)
        #     # self.update_image(self._display_size)
        #     self._image.scaled(self._display_size[0], self._display_size[1])
        #     pix = QPixmap(self._image)
        #     self._label.setPixmap(pix)
        #     self._label.setFixedSize(self._display_size[0] - 10, self._display_size[1] - 10)

        print(f"Minimum ->>> {self.minimumSize()}")
        print(size)

    def update_image(self, frame) -> None:
        resized_frame = cv2.resize(frame, self._display_size)
        print(self._display_size)
        self._image = QImage(
            resized_frame, resized_frame.shape[1], resized_frame.shape[0], QImage.Format_Grayscale8
        )
        pix = QPixmap(self._image)
        self.setPixmap(pix)
        # self.setFixedSize(self._display_size[0], self._display_size[1])