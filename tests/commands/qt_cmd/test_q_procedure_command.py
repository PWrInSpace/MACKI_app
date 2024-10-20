import pytest
from PySide6.QtWidgets import QLabel, QPushButton, QCheckBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest, QSignalSpy

from src.commands.qt_cmd import QLockCmd
from src.utils.qt import QSerialCmdLay

CMD_NAME = "test_cmd"
CMD_COLUMNS_NB = 5


@pytest.fixture
def q_serial_cmd():
    return QLockCmd(CMD_NAME, CMD_COLUMNS_NB)


def test_init_invalid_columns_nb():
    with pytest.raises(ValueError):
        QLockCmd(CMD_NAME, 2)


def test_init_pass(q_serial_cmd):
    assert q_serial_cmd._name == CMD_NAME
    assert q_serial_cmd._args == []
    assert isinstance(q_serial_cmd._unlocked_timer, QTimer)
    assert q_serial_cmd._unlocked_timer.isSingleShot() is True
    assert q_serial_cmd._unlocked_timer.isActive() is False


def test_create_gui(q_serial_cmd):
    assert isinstance(q_serial_cmd.layout(), QSerialCmdLay)

    name_layout = q_serial_cmd.layout().itemAt(0).widget()
    assert isinstance(name_layout, QLabel)
    assert name_layout.text() == CMD_NAME

    check_box = q_serial_cmd.layout().itemAt(1).widget()
    assert isinstance(check_box, QCheckBox)
    assert check_box.text() == QLockCmd.LOCK_UNCHECKED

    send_button = q_serial_cmd.layout().itemAt(2).widget()
    assert isinstance(send_button, QPushButton)
    assert send_button.text() == QLockCmd.SEND_BUTTON_TEXT
    assert send_button.isEnabled() is False


def test_send_lock_stage_changed(q_serial_cmd):
    # simulate the user checking and unchecking the lock box (checkbox)
    unlock_spy = QSignalSpy(q_serial_cmd.unlocked)
    lock_spy = QSignalSpy(q_serial_cmd.locked)

    send_lock_widget = q_serial_cmd._send_lock_widget
    send_lock_widget.setChecked(True)

    assert q_serial_cmd._send_button.isEnabled() is True
    assert send_lock_widget.isChecked() is True
    assert send_lock_widget.text() == QLockCmd.LOCK_CHECKED
    assert q_serial_cmd._unlocked_timer.isActive() is True
    assert unlock_spy.count() == 1
    assert lock_spy.count() == 0

    send_lock_widget.setChecked(False)
    assert q_serial_cmd._send_button.isEnabled() is False
    assert send_lock_widget.isChecked() is False
    assert q_serial_cmd._send_lock_widget.text() == QLockCmd.LOCK_UNCHECKED
    assert q_serial_cmd._unlocked_timer.isActive() is False
    assert lock_spy.count() == 1
    assert unlock_spy.count() == 1


def test_sendlock_autolock(q_serial_cmd):
    q_serial_cmd.UNLOCK_TIMER_TIMEOUT = 10
    unlock_spy = QSignalSpy(q_serial_cmd.unlocked)
    lock_spy = QSignalSpy(q_serial_cmd.locked)

    send_lock_widget = q_serial_cmd._send_lock_widget
    send_lock_widget.setChecked(True)

    assert q_serial_cmd._send_button.isEnabled() is True
    assert send_lock_widget.isChecked() is True
    assert send_lock_widget.text() == QLockCmd.LOCK_CHECKED
    assert q_serial_cmd._unlocked_timer.isActive() is True
    assert unlock_spy.count() == 1
    assert lock_spy.count() == 0

    QTest.qWait(q_serial_cmd.UNLOCK_TIMER_TIMEOUT + 50)
    assert q_serial_cmd._send_button.isEnabled() is False
    assert send_lock_widget.isChecked() is False
    assert send_lock_widget.text() == QLockCmd.LOCK_UNCHECKED
    assert q_serial_cmd._unlocked_timer.isActive() is False
    assert lock_spy.count() == 1
    assert unlock_spy.count() == 1


def test_send_button_clicked(q_serial_cmd):
    signal_spy = QSignalSpy(q_serial_cmd.send_clicked)
    unlock_spy = QSignalSpy(q_serial_cmd.unlocked)
    lock_spy = QSignalSpy(q_serial_cmd.locked)

    send_lock_widget = q_serial_cmd._send_lock_widget
    send_lock_widget.setChecked(True)

    QTest.mouseClick(q_serial_cmd._send_button, Qt.MouseButton.LeftButton)

    assert signal_spy.count() == 1
    assert signal_spy.at(0)[0] == "test_cmd\n\r"

    QTest.qWait(5)  # wait for the event loop to process the signal
    assert q_serial_cmd._send_button.isEnabled() is False
    assert send_lock_widget.isChecked() is False
    assert send_lock_widget.text() == QLockCmd.LOCK_UNCHECKED
    assert q_serial_cmd._unlocked_timer.isActive() is False
    assert signal_spy.count() == 1
    assert unlock_spy.count() == 1
    assert lock_spy.count() == 1
