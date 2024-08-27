import numpy as np
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger("handlers")

class BasicHandler(QObject):
    started = Signal()
    stopped = Signal()

    def __init__(self) -> None:
        super().__init__()

    def start(self):
        print("Basic handler started emit")
        self.started.emit()
        print(self)

    def stop(self):
        self.stopped.emit()

    def add_frame(self, frame: np.array):
        raise NotImplementedError("add_frame method must be implemented")

    @property
    def is_running(self) -> bool:
        raise NotImplementedError("is_running property must be implemented")