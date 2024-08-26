import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QSize, Qt

class DiagonalResizeWindow(QMainWindow):
    def __init__(self, aspect_ratio=16/9):
        super().__init__()

        # Set the aspect ratio (width / height)
        self.aspect_ratio = aspect_ratio

        # Example content: A QLabel
        label = QLabel("Diagonal Resize Only", self)
        label.setAlignment(Qt.AlignCenter)

        # Set a layout to the central widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(label)
        self.setCentralWidget(central_widget)

        # Set an initial size for the window
        initial_width = 640
        initial_height = int(initial_width / self.aspect_ratio)
        self.resize(initial_width, initial_height)

        # Flag to prevent recursion
        self.resizing = False

    def resizeEvent(self, event):
        if not self.resizing:
            self.resizing = True

            # Get the current size
            current_size = event.size()

            # Calculate the height based on the new width and the aspect ratio
            new_height = int(current_size.width() / self.aspect_ratio)

            # Set the new size, maintaining the aspect ratio
            self.resize(current_size.width(), new_height)

            self.resizing = False

        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the main window with a 16:9 aspect ratio
    window = DiagonalResizeWindow(aspect_ratio=16/9)
    window.show()

    sys.exit(app.exec())
