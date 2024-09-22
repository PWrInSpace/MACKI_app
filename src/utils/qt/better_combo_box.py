from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox


class BetterComboBox(QComboBox):
    clicked = Signal()

    def showPopup(self) -> None:
        self.clicked.emit()
        return super().showPopup()

    @property
    def pop_up_visible(self) -> bool:
        return self.view().isVisible()