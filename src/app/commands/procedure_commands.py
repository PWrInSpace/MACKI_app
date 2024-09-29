from typing import override
from PySide6.QtWidgets import QVBoxLayout, QFrame
from src.commands.qt_cmd_group import QCmdGroup
from src.commands.qt_cmd import QProcedureCmd


class ProcedureCommands(QCmdGroup):
    COLUMNS_NUM = 3
    MOTION_COMMAND = "Motion procedure"
    PRESSURE_COMMAND = "Pressurization procedure"
    TEST_COMMAND = "Test procedure"
    MAIN_COMMAND = "Main procedure"

    def __init__(self, protocol):
        commands = {
            self.MOTION_COMMAND: QProcedureCmd(self.MOTION_COMMAND, self.COLUMNS_NUM),
            self.PRESSURE_COMMAND: QProcedureCmd(
                self.PRESSURE_COMMAND, self.COLUMNS_NUM
            ),
            self.TEST_COMMAND: QProcedureCmd(self.TEST_COMMAND, self.COLUMNS_NUM),
            self.MAIN_COMMAND: QProcedureCmd(self.MAIN_COMMAND, self.COLUMNS_NUM),
        }
        super().__init__("Procedure Commands", commands, protocol)

        commands[self.MAIN_COMMAND].set_args_list(["123", "skibidi"])

        for command in commands.values():
            command.unlocked.connect(self._on_command_unlock)

    def _on_command_unlock(self, name: str):
        for command in self._commands.values():
            if command.name != name:
                command.set_locked()

    def _add_command_to_layout(self, layout, command):
        layout.addWidget(command)
        command.send_clicked.connect(self._on_send_clicked)

    @override
    def _init_ui(self):
        layout = QVBoxLayout()

        commands_list = list(self._commands.values())
        for command in commands_list[:-1]:
            self._add_command_to_layout(layout, command)

        horizontal_bar = QFrame()
        horizontal_bar.setFrameShape(QFrame.HLine)
        horizontal_bar.setFrameShadow(QFrame.Sunken)
        layout.addWidget(horizontal_bar)

        self._add_command_to_layout(layout, commands_list[-1])

        self.setLayout(layout)
