from PySide6.QtCore import QMutex


class ThreadEvent:
    def __init__(self) -> None:
        self._event_mutex = QMutex()
        self._event_flag = False

    def set(self) -> bool:
        self._event_mutex.lock()
        self._event_flag = True
        self._event_mutex.unlock()

    def restart(self) -> bool:
        self._event_mutex.lock()
        self._event_flag = False
        self._event_mutex.unlock()

    def happens(self) -> bool:
        self._event_mutex.lock()
        happens = self._event_flag
        self._event_mutex.unlock()

        return happens
