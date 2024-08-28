import numpy as np
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QCloseEvent, QImage, QPainter
from PySide6.QtWidgets import QWidget


class ImageDisplayWindow(QWidget):
    close_event = Signal()

    def __init__(
        self,
        name: str,
        default_size: tuple[int, int] = (600, 600),
        minimum_size: tuple[int, int] = (200, 200),
        format: QImage.Format = QImage.Format_Grayscale8,
    ) -> None:
        """ Create a window to display images.
        Args:
            name (str): The name of the window.
            minimum_size (tuple[int, int], optional): Minimum window size. Defaults to (200, 200).
            Tuples are immutable, so they are safe to store default values.
            format (QImage.Format, optional): Image format. Defaults to QImage.Format_Grayscale8.
        """
        super().__init__()
        self._minimum_size = QSize(*minimum_size)
        self._default_size = QSize(*default_size)
        self._format = format
        self._image = None


        self.setWindowTitle(name)
        self.setMinimumSize(self._minimum_size)

    def paintEvent(self, event):
        """ Paint event handler, this method is called when 
        the window needs to be repainted. In this event, the
        image is resized to fit the window size and then painted.
        """
        if not self._image:
            return

        windows_size = self.size()
        scaled_image = self._image.scaled(windows_size, Qt.AspectRatioMode.KeepAspectRatio)
        
        # calculate the position to center the image
        x = (windows_size.width() - scaled_image.width()) // 2
        y = (windows_size.height() - scaled_image.height()) // 2

        painter = QPainter(self)
        painter.drawImage(x, y, scaled_image)

    def resizeEvent(self, event):
        """ Resize event handler, this method is called when the window is resized.
        Inside this methode, we call the update method which will call the paintEvent,
        and the image will be resized to fit the new window size.
        """
        self.update()

    def update_image(self, frame: np.array) -> None:
        """ Update the image displayed in the window.

        Args:
            frame (np.array): image
        """
        width = frame.shape[1]
        height = frame.shape[0]
        self._image = QImage(frame, width, height, self._format)

        self.update()

    def show(self) -> None:
        """ Show the window
        """
        super().show()
        self.resize(self._default_size)

    def closeEvent(self, event: QCloseEvent) -> None:
        """ This method emits the close_event signal, to signalize that the window was
        closed by the user.

        Args:
            event (QCloseEvent): The close event
        """
        self.close_event.emit()
        return super().closeEvent(event)
        
