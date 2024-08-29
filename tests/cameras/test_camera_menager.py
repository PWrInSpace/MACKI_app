import pytest
from vmbpy import CameraEvent
from src.cameras import CamerasMenager, CamerasMenagerState
from src.cameras.camera_handler import CameraHandler
from tests.cameras.mocks import VmbMock, VmbCameraMock, VmbInstance


class CamerasMenagerMock(CamerasMenager):
    def __init__(self) -> None:
        super().__init__()
        self._instance = VmbInstance()

    def _get_vmb_instance(self) -> VmbInstance:
        # create a new instance each time
        return self._instance


@pytest.fixture
def cameras_menager() -> CamerasMenagerMock:
    return CamerasMenagerMock()


def test_cameras_menager_constructor(cameras_menager: CamerasMenagerMock):
    # check default values
    assert cameras_menager.get_state() == CamerasMenagerState.IDLE
    assert cameras_menager._cameras_handlers == {}


@pytest.mark.parametrize(
    "state",
    [
        (CamerasMenagerState.IDLE),
        (CamerasMenagerState.RUNNING),
        (CamerasMenagerState.STOPPING),
    ],
)
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


@pytest.mark.parametrize(
    "state",
    [
        (CamerasMenagerState.IDLE),
        (CamerasMenagerState.RUNNING),
        (CamerasMenagerState.STOPPING),
    ],
)
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


# test to check if mock works as intented
def test_get_vmb_instance():
    cameras_menager = CamerasMenagerMock()
    assert cameras_menager._get_vmb_instance() == cameras_menager._instance


def test_register_available_cameras():
    cameras_menager = CamerasMenagerMock()
    instance = cameras_menager._get_vmb_instance()
    assert cameras_menager._register_available_cameras(instance) == True

    cameras_id = [camera.get_id() for camera in instance.get_all_cameras()]
    assert list(cameras_menager._cameras_handlers.keys()) == cameras_id

    frames_handlers_names = [
        handler._name for handler in cameras_menager._cameras_handlers.values()
    ]
    assert list(cameras_menager._cameras_handlers.keys()) == frames_handlers_names


def test_register_available_cameras_fail():
    cameras_menager = CamerasMenagerMock()
    instance = cameras_menager._get_vmb_instance()
    instance._cameras = []
    assert cameras_menager._register_available_cameras(instance) == False
    assert cameras_menager._cameras_handlers == {}


def test_on_camera_detected_new_camera():
    cameras_menager = CamerasMenagerMock()

    name = "camera_foo"
    camera = VmbCameraMock(name)
    cameras_menager._on_camera_detected(camera)
    assert name in cameras_menager._cameras_handlers
    assert cameras_menager._cameras_handlers[name].isRunning() is True


def test_on_camera_detected_existing():
    cameras_menager = CamerasMenagerMock()

    name = "camera_foo"
    camera = VmbCameraMock(name)
    cameras_menager._cameras_handlers[name] = CameraHandler(name)
    cameras_menager._on_camera_detected(camera)

    # should not create a new CameraHandler
    assert len(cameras_menager._cameras_handlers) == 1


def test_on_camera_missing_remove():
    cameras_menager = CamerasMenagerMock()

    name = "camera_foo"
    camera = VmbCameraMock(name)
    cameras_menager._on_camera_detected(camera)

    # store reference to frame handler
    frame_handler_ref = cameras_menager._cameras_handlers[name]

    cameras_menager._on_camera_missing(camera)

    # check that handler for missing camera is deleted from dict
    assert len(cameras_menager._cameras_handlers) == 0

    # check that camera handler thread finished
    assert frame_handler_ref.isRunning() is False


def test_on_camera_missing_unknown_id():
    cameras_menager = CamerasMenagerMock()

    name = "camera_foo"
    camera = VmbCameraMock(name)
    cameras_menager._on_camera_detected(camera)

    # store reference to frame handler
    frame_handler_ref = cameras_menager._cameras_handlers[name]

    missing_name = "camera_bar"
    missing_camera = VmbCameraMock(missing_name)
    cameras_menager._on_camera_missing(missing_camera)

    # check that all previous handlers are present
    assert len(cameras_menager._cameras_handlers) == 1

    # check that camera handler thread is still running
    assert frame_handler_ref.isRunning() is True


@pytest.mark.parametrize("camera_event", [(e.value) for e in CameraEvent])
def test_camera_change_handler_calls(mocker, camera_event):
    # in case that new camera event was added to vmbpy lib
    spy_detected = mocker.spy(CamerasMenagerMock, "_on_camera_detected")
    spy_missing = mocker.spy(CamerasMenagerMock, "_on_camera_missing")

    cameras_menager = CamerasMenagerMock()
    camera = VmbCameraMock("camera_foo")
    cameras_menager._camera_change_handler(camera, camera_event)

    match camera_event:
        case CameraEvent.Detected:
            assert spy_detected.call_count == 1
            assert spy_missing.call_count == 0
        case CameraEvent.Missing:
            assert spy_detected.call_count == 0
            assert spy_missing.call_count == 1
        case _:
            assert spy_detected.call_count == 0
            assert spy_missing.call_count == 0


@pytest.mark.parametrize("camera_event", [(e.value) for e in CameraEvent])
def test_camera_change_handler_signal(mocker, camera_event):
    stub = mocker.stub()

    cameras_menager = CamerasMenagerMock()
    cameras_menager.cameras_changed.connect(stub)

    camera = VmbCameraMock("camera_foo")
    cameras_menager._camera_change_handler(camera, camera_event)

    match camera_event:
        case CameraEvent.Detected:
            assert stub.called
        case CameraEvent.Missing:
            assert stub.called
        case _:
            assert not stub.called


def test_start_cameras() -> None:
    cameras_menager = CamerasMenagerMock()
    vmb = cameras_menager._get_vmb_instance()
    cameras_menager._register_available_cameras(vmb)

    for handler in cameras_menager._cameras_handlers.values():
        assert handler.isRunning() is False

    cameras_menager._start_cameras()

    for handler in cameras_menager._cameras_handlers.values():
        assert handler.isRunning() is True


def test_register_vmb_callbacks(mocker):
    handler_spy = mocker.spy(CamerasMenagerMock, "_camera_change_handler")

    vmb = VmbInstance()

    cameras_menager = CamerasMenagerMock()
    cameras_menager._register_vmb_callbacks(vmb)

    camera = vmb._cameras[0]
    vmb.emit_camera_change(camera, CameraEvent.Unknown)

    assert handler_spy.call_count == 1
    assert handler_spy.call_args[0][1] == camera
    assert handler_spy.call_args[0][2] == CameraEvent.Unknown


def test_unregister_vmb_callbacks(mocker):
    handler_spy = mocker.spy(CamerasMenagerMock, "_camera_change_handler")

    vmb = VmbInstance()

    cameras_menager = CamerasMenagerMock()
    cameras_menager._register_vmb_callbacks(vmb)
    cameras_menager._unregister_vmb_callbacks(vmb)

    vmb.emit_camera_change(VmbCameraMock("test"), CameraEvent.Unknown)

    assert handler_spy.call_count == 0


def test_clean_up_menager():
    cameras_menager = CamerasMenagerMock()

    vmb = cameras_menager._get_vmb_instance()
    cameras_menager._register_available_cameras(vmb)
    cameras_menager._start_cameras()

    # assert if there is no cameras
    assert len(cameras_menager._cameras_handlers) > 0

    handlers_ref = cameras_menager._cameras_handlers.copy()

    cameras_menager._clean_up_menager()

    # check that menager does not have any frame handlers
    assert len(cameras_menager._cameras_handlers) == 0

    # check that frame handlers are not running
    assert all([h.isRunning() == False for h in handlers_ref.values()])


def test_wait_until_stop_signal():
    pass


def test_raise_error():
    pass


@pytest.mark.parametrize(
    "initial_state, expected",
    [(CamerasMenagerState.IDLE, False), (CamerasMenagerState.RUNNING, True)],
)
def test_terminate_thread(initial_state, expected):
    cameras_menager = CamerasMenagerMock()
    cameras_menager._change_state(initial_state)

    assert cameras_menager.terminate_thread() is expected

    if expected:
        assert cameras_menager.get_state() == CamerasMenagerState.STOPPING
    else:
        assert cameras_menager.get_state() == initial_state


# def test_cameras_registered_signal(cameras_menager: CamerasMenagerMock):
#     signal = cameras_menager.cameras_registered
#     assert signal is not None
#     assert signal.receivers() == 0

#     signal.connect(lambda: None)
#     assert signal.receivers() == 1

#     signal.disconnect()
#     assert signal.receivers() == 0
