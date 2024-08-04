import numpy as np
from abc import ABC, abstractmethod


class BasicHandler(ABC):
    @abstractmethod
    def add_frame(self, frame: np.array):
        pass
