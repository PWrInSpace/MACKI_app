from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from src.com.abstract import ComProtoBasic
from src.procedures.procedure_plot import ProcedurePlot

class ProceduresWidget(QWidget):
    BUTTON_TXT_START = "Start"
    BUTTON_TXT_STOP = "Stop"

    def __init__(self, protocol: ComProtoBasic | None = None):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Procedures")
        self.layout.addWidget(self.label)

        self._procedure_button = QPushButton(self.BUTTON_TXT_START)
        self._procedure_button.setStyleSheet("background-color: green")
        self._procedure_button.clicked.connect(self._on_procedure_button_clicked)
        self.layout.addWidget(self._procedure_button)

        self.setFixedSize(500, 300)
        self._plot = ProcedurePlot()
        self.layout.addWidget(self._plot)


    def _on_procedure_button_clicked(self):
        if self._procedure_button.text() == self.BUTTON_TXT_START:
            self._procedure_button.setText(self.BUTTON_TXT_STOP)
            self._procedure_button.setStyleSheet("background-color: red")
        else:
            self._procedure_button.setText(self.BUTTON_TXT_START)
            self._procedure_button.setStyleSheet("background-color: green")
