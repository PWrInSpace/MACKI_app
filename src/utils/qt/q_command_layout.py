from typing import override
from PySide6.QtWidgets import QGridLayout, QWidget


class QSerialCmdLay(QGridLayout):
    ROW = 0
    STRETCH = 1

    def __init__(self, number_of_columns: int) -> None:
        """Create a new QSerialCmdLay

        Args:
            number_of_columns (int): Number of columns in the layout
        """
        super().__init__()
        self._column_position = 0
        self._args_set = False
        self._number_of_columns = number_of_columns

    @override
    def addWidget(self, widget: QWidget) -> None:
        """Add widget to the layout

        Args:
            widget (QWidget): Widget to add

        Raises:
            ValueError: Cannot add more widgets than the number of columns
        """
        # we left one column for the send button
        if self._number_of_columns <= self._column_position:
            raise ValueError("Cannot add more widgets than the number of columns")

        super().addWidget(widget, self.ROW, self._column_position)
        self._column_position += 1

    def addWidgetBeforeArgs(self, widget: QWidget) -> None:
        """Add widget before the last column

        Args:
            widget (QWidget): Widget to add

        Raises:
            ValueError: Not enough columns to add the widget
        """
        if self._args_set:
            raise ValueError("Cannot add, args already set")

        self.addWidget(widget)

    def addArgWidgets(self, widgets: QWidget) -> None:
        """Add widgets before the last column

        Args:
            widgets (QWidget): Widgets to add

        Raises:
            ValueError: Not enough columns to add all widgets
        """
        args_nb = len(widgets)
        # we left one column for the last widget
        collumns_left_for_args = (self._number_of_columns - 1) - self._column_position

        if args_nb > collumns_left_for_args:
            raise ValueError("Not enough columns to add all widgets")

        # Uncomment this line to shift the args to the right
        # self._column_position = collumns_left_for_args - args_nb
        for widget in widgets:
            self.addWidget(widget)

        self._args_set = True

    def addLastWidget(self, widget: QWidget) -> None:
        """Add widget to the last column

        Args:
            widget (QWidget): Widget to add
        """
        if self._column_position >= self._number_of_columns:
            raise ValueError("Cannot add more widgets than the number of columns")

        self._column_position = self._number_of_columns - 1
        self.addWidget(widget)

    @override
    def setColumnStretch(self) -> None:
        """Set stretch for all columns"""
        for i in range(self._number_of_columns):
            super().setColumnStretch(i, self.STRETCH)
