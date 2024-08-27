import cv2
from PySide6.QtCore import QSize, QMutex, Qt, Signal
from PySide6.QtGui import QCloseEvent, QImage, QPixmap, QPainter
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QBoxLayout

class ImageDisplayWindow(QWidget):
    close_event = Signal()

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
        self._default_size = QSize(*default_size)
        self._minimum_size = QSize(*minimum_size)
        self._format = format
        self._mutex = QMutex()

        self.setWindowTitle(name)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel()
        self._label.setMinimumSize(self._minimum_size)
        self._label.setScaledContents(True)
        layout.addWidget(self._label)
        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)

        windows_size = self.size()

        scaled_image = self.image.scaled(
            windows_size,
            Qt.AspectRatioMode.KeepAspectRatio
        )

        x = (windows_size.width() - scaled_image.width()) // 2
        y = (windows_size.height() - scaled_image.height()) // 2

        painter.drawImage(x, y, scaled_image)

    def resizeEvent(self, event):
        self.update()

    def update_image(self, frame) -> None:
        self.image = QImage(
            frame,
            frame.shape[1],
            frame.shape[0],
            QImage.Format_Grayscale8    # TBD
        )
        self.update()

    def show(self):
        super().show()
        self.resize(self._default_size)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.close_event.emit()
        return super().closeEvent(event)