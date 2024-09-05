from PySide6.QtCore import QMutex


class ThreadEvent:
    def __init__(self) -> None:
        """Constructor for the ThreadEvent class."""
        self._event_mutex = QMutex()
        self._event_flag = False

    def set(self) -> None:
        """Set the event flag to True."""
        self._event_mutex.lock()
        self._event_flag = True
        self._event_mutex.unlock()

    def clear(self) -> None:
        """Restart the event
        Set the event flag to False.
        """
        self._event_mutex.lock()
        self._event_flag = False
        self._event_mutex.unlock()

    def occurs(self) -> bool:
        """Check if the event occurs.

        Returns:
            bool: True if the event occurs, False otherwise.
        """
        self._event_mutex.lock()
        occurs = self._event_flag
        self._event_mutex.unlock()

        return occurs
