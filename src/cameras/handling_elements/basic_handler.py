import numpy as np
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger("handlers")

class BasicHandler(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def add_frame(self, frame: np.array):
        pass
