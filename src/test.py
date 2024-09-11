import sys
from PySide6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create a QTextEdit widget
        self.text_edit = QTextEdit(self)

        # Add some example text
        self.text_edit.setPlainText(
            "This is a QTextEdit widget with scrolling enabled.\n" * 30
        )
        self.text_edit

        # Create a layout and add the QTextEdit widget to it
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)

        # Set the layout on the main window
        self.setLayout(layout)
        self.setWindowTitle("QTextEdit with Scrollbars - PySide6")

        # Show scrollbars when content exceeds the visible area (this is the default behavior)
        self.text_edit.setLineWrapMode(
            QTextEdit.NoWrap
        )  # Disable word wrapping for horizontal scrolling
        self.text_edit.setTextColor(Qt.red)
        self.text_edit.append("New line added.\n")
        self.text_edit.setTextColor(Qt.blue)
        self.text_edit.insertPlainText("New line added.\n")
        self.scroll_to_bottom()

        # Optional: Set scrollbars to always be visible or not
        # self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Move the scrollbar to the bottom
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        # Ensure the scrollbar is at the bottom
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.minimum())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow()
    window.resize(400, 300)
    window.show()

    # Execute the application
    sys.exit(app.exec())
