from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QGroupBox, QComboBox, QPushButton, QGridLayout
from src.com.abstract import ComProtoBasic
from src.procedures.procedure_plot import ProcedurePlot
# from src.commands.qt_cmd.q_lock_command import QLockCmd
from src.procedures.procedure_command import ProcedureCmd


class ProceduresWidget(QGroupBox):
    BUTTON_TXT_START = "Start"
    BUTTON_TXT_STOP = "Stop"

    def __init__(self, protocol: ComProtoBasic | None = None):
        super().__init__("Procedure control")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        label = QLabel("Procedure name")
        procedure_type = QComboBox()
        procedure_type.addItems(["Procedure 1", "Procedure 2", "Procedure 3"])
        info_button = QPushButton("Procedure values")

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(procedure_type, 0, 1)
        layout.addWidget(info_button, 0, 2)
        widget = QWidget()
        widget.setLayout(layout)

        horizontal_bar = QFrame()
        horizontal_bar.setFrameShape(QFrame.HLine)
        horizontal_bar.setFrameShadow(QFrame.Sunken)

        # self.setFixedSize(500, 500)
        self._plot = ProcedurePlot()
        self.layout.addWidget(widget)
        self.layout.addWidget(self._plot)
        self.layout.addWidget(horizontal_bar)
        self.layout.addWidget(ProcedureCmd("Procedure", 3))