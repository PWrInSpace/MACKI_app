from typing import override
from enum import Enum
from PySide6.QtCore import QObject, QThread, Signal, QMutex
from vmbpy import VmbSystem, Camera, CameraEvent

from src.cameras.camera_handler import CameraHandler, logger
from src.utils.qt.thread_event import ThreadEvent


class CamerasMenagerState(Enum):
    """Camera menager states"""

    IDLE = 0
    RUNNING = 1
    STOPPING = 2
    UNKNOW = 99


class CamerasMenager(QThread):
    camera_registered = Signal(CameraHandler)
    camera_missing = Signal(str)  # camera id

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._cameras_handlers: dict[str, CameraHandler] = {}  # check weakpointer
        self._menager_state: CamerasMenagerState = CamerasMenagerState.IDLE
        self._mutex = QMutex()
        self._stop_signal = ThreadEvent()

    def _change_state(self, state: CamerasMenagerState) -> bool:
        """Changes the state of the cameras menager.

        Args:
            state (CamerasMenagerState): The new state.
        """
        if self._mutex.try_lock() is False:
            logger.warning("Unable to change state")
            return False

        logger.info(f"Changing state from {self._menager_state} to {state}")
        self._menager_state = state
        self._mutex.unlock()

        return True

    def get_state(self) -> CamerasMenagerState:
        """Getter for camera menager state

        Returns:
            CamerasMenagerState: current state
        """
        state = CamerasMenagerState.UNKNOW
        if self._mutex.try_lock():
            state = self._menager_state
            self._mutex.unlock()
        else:
            logger.warning("Unable to lock mutex")

        return state

    def _get_vmb_instance(self) -> VmbSystem:
        """Returns a new VmbSystem instance.
        It is a separate method to allow mocking in tests.

        Returns:
            VmbSystem: The VmbSystem instance.
        """
        return VmbSystem.get_instance()

    def _register_available_cameras(self, vmb: VmbSystem) -> bool:
        """Registers all available cameras in the system.
        This methode creates a CameraHandler for each camera, where the
        name of the camera is a camera id.
        FramesHandlers are stored in the _cameras_handlers dictionary, where the key
        is the camera id.

        Args:
            vmb (VmbSystem): The VmbSystem instance.

        Returns:
            bool: True if at least one camera was registered, False otherwise.
        """
        cameras: list[Camera] = vmb.get_all_cameras()

        if not cameras:
            logger.error("No cameras available")
            return False

        for camera in cameras:
            self._on_camera_detected(camera)

        return True

    def _on_camera_detected(self, camera: Camera) -> None:
        """Handles the camera detected event.

        Args:
            camera (Camera): The camera that was detected.
        """
        camera_id = camera.get_id()

        if camera_id not in self._cameras_handlers:
            self._cameras_handlers[camera_id] = CameraHandler(camera)
            self.camera_registered.emit(self._cameras_handlers[camera_id])
        else:
            logger.warning(f"Camera {camera_id} is already in the list")

    def _on_camera_missing(self, camera: Camera) -> None:
        """Handles the camera missing event.

        Args:
            camera (Camera): The camera that is missing.
        """
        camera_id = camera.get_id()

        if camera_id in self._cameras_handlers:
            self._cameras_handlers[camera_id].quit()
            del self._cameras_handlers[camera_id]
            self.camera_missing.emit(camera_id)
        else:
            logger.warning(f"Camera {camera_id} is not in the list!")

    def _camera_change_handler(self, camera: Camera, event: CameraEvent) -> None:
        """Handles the camera change event.
        By default the lifetime of this callback is limited to the RUNNING
        state,but to leave additional message, a warning log is sent, when
        event was recived on different state than RUNNING

        Args:
            camera_id (str): The id of the camera that changed.
        """
        logger.info(f"Camera {camera.get_id()} changed")
        if self.get_state() != CamerasMenagerState.RUNNING:
            logger.warning("Camera change received in state other than running")

        match event:
            case CameraEvent.Detected:
                self._on_camera_detected(camera)
            case CameraEvent.Missing:
                self._on_camera_missing(camera)
            case CameraEvent.Reachable | CameraEvent.Unreachable:
                # we don't need to do anything here
                logger.info("Camera status changed to reachable/unreachable")
            case CameraEvent.Unknown:
                logger.warning("Unknown camera event")

    def _start_cameras(self) -> None:
        """Starts the threads for all the cameras."""
        for camera_handler in self._cameras_handlers.values():
            camera_handler.start()

    def _register_vmb_callbacks(self, vmb: VmbSystem) -> None:
        """Registers the VmbSystem callbacks.

        Args:
            vmb (VmbSystem): The VmbSystem instance.
        """
        vmb.register_camera_change_handler(self._camera_change_handler)

    def _unregister_vmb_callbacks(self, vmb: VmbSystem) -> None:
        """Unregisters the VmbSystem callbacks.

        Args:
            vmb (VmbSystem): The VmbSystem instance.
        """
        vmb.unregister_camera_change_handler(self._camera_change_handler)

    def _clean_up_menager(self) -> None:
        """Cleans up the threads for all the cameras."""
        for camera_handler in self._cameras_handlers.values():
            camera_handler.quit()

        self._cameras_handlers.clear()

    def _wait_until_stop_signal(self):
        """Waits until the stop signal is received."""
        while not self._stop_signal.occurs():
            QThread.msleep(250)

    @override
    def run(self) -> None:
        """The main loop of the cameras menager.
        It registers all available cameras, and starts vmb context.
        Then it waits until the stop signal is received.
        """
        logger.info("Cameras menager started")

        self._stop_signal.clear()
        self._change_state(CamerasMenagerState.RUNNING)
        vmb = self._get_vmb_instance()

        with vmb:
            self._register_available_cameras(vmb)

            self._register_vmb_callbacks(vmb)

            self._wait_until_stop_signal()
            self._unregister_vmb_callbacks(vmb)

        self._clean_up_menager()

        self._change_state(CamerasMenagerState.IDLE)

    @override
    def quit(self) -> None:
        """Quits the cameras menager thread."""
        if self.get_state() != CamerasMenagerState.RUNNING:
            logger.warning("Thread is not running")
            return False

        self._change_state(CamerasMenagerState.STOPPING)
        self._stop_signal.set()
        super().wait()

        logger.info("Cameras menager thread stopped")
