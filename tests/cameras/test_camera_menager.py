import pytest
from PySide6.QtCore import QThread
from src.cameras import CamerasMenager, CamerasMenagerState
from src.cameras.frames_handler import FramesHandler
from tests.cameras.mocks import VmbMock, VmbCameraMock

class CamerasMenagerMock(CamerasMenager):
    def _get_vmb_instance(self):
        return VmbMock.get_instance()

@pytest.fixture
def cameras_menager() -> CamerasMenagerMock:
    return CamerasMenagerMock()


def test_cameras_menager_constructor(cameras_menager: CamerasMenagerMock):
    # check default values
    assert cameras_menager.get_state() == CamerasMenagerState.IDLE
    assert cameras_menager._cameras == {}


@pytest.mark.parametrize("state", [
    (CamerasMenagerState.IDLE),
    (CamerasMenagerState.RUNNING),
    (CamerasMenagerState.STOPPING)
])
def test_change_state(state):
    cameras_menager = CamerasMenagerMock()
    assert cameras_menager._change_state(state) == True
    assert cameras_menager._menager_state == state


def test_change_state_fail():
    cameras_menager = CamerasMenagerMock()
    cameras_menager._mutex.lock()
    assert cameras_menager._change_state(CamerasMenagerState.RUNNING) == False
    cameras_menager._mutex.unlock()
    assert cameras_menager.get_state() == CamerasMenagerState.IDLE


@pytest.mark.parametrize("state", [
    (CamerasMenagerState.IDLE),
    (CamerasMenagerState.RUNNING),
    (CamerasMenagerState.STOPPING)
])
def test_get_state(state):
    cameras_menager = CamerasMenagerMock()
    cameras_menager._change_state(state)
    assert cameras_menager.get_state() == state


def test_get_state_fail():
    cameras_menager = CamerasMenagerMock()
    cameras_menager._mutex.lock()
    assert cameras_menager.get_state() == CamerasMenagerState.UNKNOW
    cameras_menager._mutex.unlock()
    # after unlock should return the current state
    assert cameras_menager.get_state() == CamerasMenagerState.IDLE


def test_get_vmb_instance():
    cameras_menager = CamerasMenagerMock()
    assert cameras_menager._get_vmb_instance() == VmbMock.get_instance()


def test_register_available_cameras():
    cameras_menager = CamerasMenagerMock()
    instance = cameras_menager._get_vmb_instance()
    assert cameras_menager._register_available_cameras(instance) == True

    cameras_id = [camera.get_id() for camera in instance.get_cameras()]
    assert list(cameras_menager._cameras.keys()) == cameras_id

    frames_handlers_names = [handler._name for handler in cameras_menager._cameras.values()]
    assert list(cameras_menager._cameras.keys()) == frames_handlers_names


def test_register_available_cameras_fail():
    cameras_menager = CamerasMenagerMock()
    instance = cameras_menager._get_vmb_instance()
    instance._cameras = []
    assert cameras_menager._register_available_cameras(instance) == False
    assert cameras_menager._cameras == {}


def test_on_camera_detected_new_camera():
    cameras_menager = CamerasMenagerMock()

    camera = VmbCameraMock("camera_foo")
    cameras_menager._on_camera_detected(camera)
    assert "camera_foo" in cameras_menager._cameras

    cameras_menager._cameras["camera_foo"].quit()


def test_on_camera_detected_existing():
    cameras_menager = CamerasMenagerMock()

    camera = VmbCameraMock("camera_foo")
    cameras_menager._cameras["camera_foo"] = FramesHandler("camera_foo")
    cameras_menager._on_camera_detected(camera)

    # should not create a new FramesHandler
    assert len(cameras_menager._cameras) == 1

    cameras_menager._cameras["camera_foo"].quit()



# def test_cameras_registered_signal(cameras_menager: CamerasMenagerMock):
#     signal = cameras_menager.cameras_registered
#     assert signal is not None
#     assert signal.receivers() == 0

#     signal.connect(lambda: None)
#     assert signal.receivers() == 1

#     signal.disconnect()
#     assert signal.receivers() == 0