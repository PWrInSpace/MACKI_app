import cv2
from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QBoxLayout


class ImageDisplayWindow(QWidget):
    def __init__(
            self,
            name: str,
            default_size: tuple[int, int] = (640, 480),
            minimum_size: tuple[int, int] = (200, 200),
            format: QImage.Format = QImage.Format_Grayscale8
        ) -> None:
        """ Create a window to display images.
            TODO: determine the default arguments
        Args:
            name (str): The name of the window.
            default_size (tuple[int, int], optional): Default window size. Defaults to (640, 480).
            Tuples are immutable, so they are safe to store default values.
            minimum_size (tuple[int, int], optional): Minimum window size. Defaults to (200, 200).
            format (QImage.Format, optional): Image format. Defaults to QImage.Format_Grayscale8.
        """
        super().__init__()
        self.setWindowTitle(name)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel()
        self._label.setMinimumSize(self._minimum_size)
        self._label.setScaledContents(True)
        layout.addWidget(self._label)
        self.setLayout(layout)

        self._default_size = QSize(*default_size)
        self._minimum_size = QSize(*minimum_size)
        self._format = format

    def update_image(self, frame) -> None:
        resized_frame = cv2.resize(
            frame, (self._default_size.width(), self._default_size.height())
        )

        image = QImage(
            resized_frame,
            resized_frame.shape[1],
            resized_frame.shape[0],
            QImage.Format_Grayscale8    # TBD
        )
        pix = QPixmap(image)
        self._label.setPixmap(pix)

    def show(self):
        super().show()
        self.resize(self._default_size)