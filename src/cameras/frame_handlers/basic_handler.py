import numpy as np
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger("handlers")


class BasicHandler(QObject):
    started = Signal()  # Signal emitted when the handler starts
    stopped = Signal()  # Signal emitted when the handler stops

    def __init__(self) -> None:
        """ Constructor
        """
        super().__init__()

    def start(self):
        """ Start the handler, this method emit the started signal 
        """
        self.started.emit()

    def stop(self):
        """ Stop the handler, this method emit the stopped signal
        """
        self.stopped.emit()

    def add_frame(self, frame: np.array):
        """ Add a frame to the handler

        Args:
            frame (np.array): The frame to be handled by the handler

        Raises:
            NotImplementedError: This method must be implemented
        """
        raise NotImplementedError("add_frame method must be implemented")

    @property
    def is_running(self) -> bool:
        """ Check if the handler is running

        Raises:
            NotImplementedError: This property must be implemented

        Returns:
            bool: True if the handler is running, False otherwise
        """
        raise NotImplementedError("is_running property must be implemented")
