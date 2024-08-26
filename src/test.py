from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize

class ResizableLabel(QLabel):
    def __init__(self, pixmap):
        super().__init__()
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.aspect_ratio = pixmap.width() / pixmap.height()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(100, 100)  # Minimum size to prevent it from shrinking too much

    def resizeEvent(self, event):
        current_width = self.width()
        new_height = int(current_width / self.aspect_ratio)
        print(f"Current width: {current_width}, New height: {new_height}")
        self.setFixedSize(QSize(current_width, new_height))
        super().resizeEvent(event)

app = QApplication([])

window = QWidget()
layout = QVBoxLayout()

pixmap = QPixmap("dark_img.jpg")
label = ResizableLabel(pixmap)

label.resize(300, int(300 / label.aspect_ratio))  # Set an initial size

layout.addWidget(label)

window.setLayout(layout)
window.show()

app.exec()
