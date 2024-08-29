from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout
from PySide6.QtCore import Slot
from src.cameras.frame_handlers import BasicHandler, FrameDisplay, VideoWriter
from src.app.camera_widget_utils import CameraStatus, STATUS_TO_COLOR
from src.cameras.q_camera import QCamera
from typing import override

DISPLAY_BUTTON_OPEN = "Open"
DISPLAY_BUTTON_CLOSE = "Close"


class QCameraWidget(QCamera):
    """ Widget created for the MACKI app project.
    """
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
        """ Constructor

        Args:
            name (str): camera name
            id (str): camera id
            handlers (list[BasicHandler]): list of handlers
            camera_config_file (str, optional): camera config file. Defaults to None.
        """
        # The handlers will be loaded later, so we pass None
        super().__init__(name, id, None, camera_config_file)
        
        self._load_handlers(handlers)
        self._connect_to_frame_display_signals()
        
        self.update_status()

    def _load_handlers(self, handlers: list[BasicHandler]):
        """ Load the handlers

        Args:
            handlers (list[BasicHandler]): list of handlers

        Raises:
            ValueError: Unknown handler type
            ValueError: No display handler found
            ValueError: No writer handler found
        """
        self._handlers = {
            self.HANDLER_DISPLAY: None,
            self.HANDLER_WRITER: None,
        }

        for handler in handlers:
            if isinstance(handler, FrameDisplay):
                self._handlers[self.HANDLER_DISPLAY] = handler
            elif isinstance(handler, VideoWriter):
                self._handlers[self.HANDLER_WRITER] = handler
            else:
                raise ValueError(f"Unknown handler type: {handler}")

        if not self._handlers[self.HANDLER_DISPLAY]:
            raise ValueError("No display handler found")
        if not self._handlers[self.HANDLER_WRITER]:
            raise ValueError("No writer handler found")

    def _connect_to_frame_display_signals(self):
        """ Connect to the frame display signals
        """
        self._handlers[self.HANDLER_DISPLAY].close_event.connect(
            self._on_frame_display_close_event
        )

    def _on_frame_display_close_event(self):
        """ Handle the frame display close event """
        self.display_button.setText(DISPLAY_BUTTON_OPEN)
        self.update_status()

    @override
    def _create_qui_elements(self):
        """Create GUI elements for the camera, this class is not a widget,
        so it contains only the layout elements. It was created like this to
        set this elements on grid in the QCamerasMenager class.
        """
        self.name_label = QLabel(f"{self.name}:")
        self.status_label = QLabel()

        self.display_button = QPushButton("Open")
        self.display_button.clicked.connect(self._on_open_button_clicked)

        self.write_button = QPushButton("Write")
        self.write_button.clicked.connect(self._on_write_button_clicked)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.display_button)
        self.layout.addWidget(self.write_button)

        self.setLayout(self.layout)

    def _on_write_button_clicked(self):
        if self.write_button.text() == "Write":
            self.write_button.setText("Stop")
            self.handlers[self.HANDLER_WRITER].start()
        else:
            self.write_button.setText("Write")
            self.handlers[self.HANDLER_WRITER].stop()

        self.update_status()

    def _on_open_button_clicked(self):
        """ Open or close the display window.
        """
        if self.display_button.text() == DISPLAY_BUTTON_OPEN:
            self.display_button.setText(DISPLAY_BUTTON_CLOSE)
            self.handlers[self.HANDLER_DISPLAY].start()
        else:
            self.display_button.setText(DISPLAY_BUTTON_OPEN)
            self.handlers[self.HANDLER_DISPLAY].stop()

        self.update_status()

    def _update_gui(self, status: CameraStatus):
        """ Update the GUI elements
        """
        if status == CameraStatus.MISSING:
            self.display_button.setEnabled(False)
            self.write_button.setEnabled(False)
        else:
            self.display_button.setEnabled(True)
            self.write_button.setEnabled(True)

    @override
    def update_status(self):
        status = self.get_str_status()
        self.status_label.setText(status.value)
        self.status_label.setStyleSheet(f"color: {STATUS_TO_COLOR[status]}")

        self._update_gui(status)
        

    def get_str_status(self) -> str:
        handlers_states = {k: v.is_running for k, v in self.handlers.items()}

        if not self._detected:
            status = CameraStatus.MISSING
        elif handlers_states[self.HANDLER_DISPLAY] and\
             handlers_states[self.HANDLER_WRITER]:
            status = CameraStatus.WRITING_AND_DISPLAYING
        elif handlers_states[self.HANDLER_DISPLAY]:
            status = CameraStatus.DISPLAYING
        elif handlers_states[self.HANDLER_WRITER]:
            status = CameraStatus.WRITING
        elif self._running:
            status = CameraStatus.RUNNING
        elif self._detected:
            status = CameraStatus.DETECTED
        else:
            status = CameraStatus.UNKNOWN

        return status
    
    @override
    @property
    def handlers(self) -> dict[int, BasicHandler]:
        return self._handlers
