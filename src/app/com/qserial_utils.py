from enum import Enum
from typing import override
from PySide6.QtCore import QThread
from src.utils.qt.thread_event import ThreadEvent
from src.com.serial_port import Serial


class QSerialState(Enum):
    """This class represents the MacusWidget state
    """
    DISCONNECTED = 0
    CONNECTED = 1
    MISSING = 2
    UNKNOWN = 99


class SerialStateControlThread(QThread):
    """ To avoid inheriting from the QThread class in QSerial, we create a
    separate thread class that controls the state of the given QSerial object.
    To avoid race conditions the state is protected by a mutex in the QSerial class.

    Args:
        QThread: The QThread class
    """
    def __init__(self, serial: Serial) -> None:
        """ This method initializes the SerialStateControlThread class

        Args:
            serial (Serial): The serial object
        """
        super().__init__()
        self._serial = serial
        self._thread_stop = ThreadEvent()

    def run(self) -> None:
        """ This method runs the thread
        """
        while not self._thread_stop.occurs():
            self._serial._state_control_loop()

    @override
    def terminate(self) -> None:
        """ This method terminates the thread
        """
        self._thread_stop.set()
