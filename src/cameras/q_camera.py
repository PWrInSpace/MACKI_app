from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout
from PySide6.QtCore import Slot
from src.cameras.frame_handlers import BasicHandler


class QCamera(QWidget):
    HANDLER_DISPLAY = 0
    HANDLER_WRITER = 1
    HANDLER_UNKNOWN = 99

    def __init__(
        self,
        name: str,
        id: str,
        handlers: list[BasicHandler],
        camera_config_file:str = None
    ) -> None:
        super().__init__()

        self._name = name
        self._id = id
        self._config_file = camera_config_file
        self._handlers = handlers

        self._detected = False
        self._running = False

        self._create_qui_elements()

    def _create_qui_elements(self):
        """ Create the GUI elements for the camera widget.
        Which allows the user to control the camera handlers.

        Raises:
            NotImplementedError: This method should be implemented in a subclass
        """
        raise NotImplementedError("This method should be implemented in a subclass")

    ### END GUI ###
    def update_status(self):
        """Update the status of the cameras on the widget.
        This method should be implemented in a subclass.
        """
        raise NotImplementedError("This method should be implemented in a subclass")

    def set_detected_flag(self, detected: bool):
        """This method is used to set the detected flag. This class only knows states
        of the handlers, not the camera itself.
        Handlers are connected to cameras and they only receive frames from them.

        Args:
            detected (bool): True if the camera is detected, False otherwise
        """
        self._detected = detected

    @Slot()
    def on_camera_thread_started(self) -> None:
        self._running = True

    @Slot()
    def on_camera_thread_finished(self) -> None:
        self._running = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> str:
        return self._id

    @property
    def handlers(self) -> list[BasicHandler]:
        return self._handlers
    
    @property
    def config_file(self) -> str:
        return self._config_file