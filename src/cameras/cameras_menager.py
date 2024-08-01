import logging
from PySide6.QtCore import QObject, QThread, Signal
from vmbpy import (
    VmbSystem,
    Camera,
    CameraEvent
)

from src.cameras.camera import CameraHandler

from enum import Enum

logger = logging.getLogger("cameras")

# add cameras menager states

class CamerasMenagerState(Enum):
    IDLE = 0
    RUNNING = 1
    STOPPING = 2


class CamerasMenager(QThread):
    cameras_registered = Signal()
    cameras_changed = Signal()

    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        self._cameras: dict[str, CameraHandler]  # check weakpointer
        self._cameras_state: CamerasMenagerState = CamerasMenagerState.IDLE

    def _change_state(self, state: CamerasMenagerState) -> None:
        """Changes the state of the cameras menager.

        Args:
            state (CamerasMenagerState): The new state.
        """
        self._cameras_state = state

    def _get_vmb_instance(self) -> VmbSystem:
        """Returns a new VmbSystem instance.
        It is a separate method to allow mocking in tests.

        Returns:
            VmbSystem: The VmbSystem instance.
        """
        return VmbSystem.get_instance()

    def _register_available_cameras(self, vmb: VmbSystem) -> bool:
        """ Registers all available cameras in the system.

        Args:
            vmb (VmbSystem): The VmbSystem instance.

        Returns:
            bool: True if at least one camera was registered, False otherwise.
        """
        cameras: list[Camera] = vmb.get_cameras()

        if not cameras:
            logger.error("No cameras available")
            return False

        for camera in cameras:
            self._cameras[camera.get_id()] = CameraHandler(camera)

        return True

    def _camera_change_handler(self, camera: Camera, event: CameraEvent) -> None:
        """Handles the camera change event.

        Args:
            camera_id (str): The id of the camera that changed.
        """
        logger.info(f"Camera {camera.get_id()} changed")

        match event:
            case CameraEvent.Detected:
                # TODO: Check if camera is already in the list
                # TODO: check state of cameras menager
                # ?self._cameras[camera.get_id()] = CameraHandler(camera)

                pass
            case CameraEvent.Missing:
                # TODO check state of cameras menager
                # stop thread
                # self._cameras.pop(camera.get_id())
                pass
            case _:
                logger.warning("Unknown camera event")

        self.cameras_changed.emit()

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

    def _start_cameras_threads(self) -> None:
        """Starts the threads for all the cameras.
        """
        for camera_handler in self._cameras.values():
            camera_handler.start()

    def _clean_up_menager(self) -> None:
        """Cleans up the threads for all the cameras.
        """
        for camera_handler in self._cameras.values():
            camera_handler.stop()

        # Wait for shutdown to complete
        for camera_handler in self._cameras.values():
            camera_handler.join()

        # Clear the cameras dictionary
        self._cameras.clear()

    def raise_error(self, error: Exception) -> None:
        """Raises an error in the cameras menager.

        Args:
            error (Exception): The error to raise.
        """
        # check if cameras are running

        logger.error(f"Error: {error}")
        self._change_state(CamerasMenagerState.IDLE)
        raise error

    def run(self) -> None:
        logger.info("Cameras menager started")

        self._change_state(CamerasMenagerState.RUNNING)
        vmb = self._get_vmb_instance()

        with vmb:
            if not self._register_available_cameras(vmb):
                self.raise_error(RuntimeError("No cameras available, exiting thread"))

            self.cameras_registered.emit()

            self._register_vmb_callbacks(vmb)
            self._start_cameras_threads()

            # wait until stop signal
            # self._wait_unitl_stop()

            # self._unregister_vmb_callbacks(vmb)
            # self._clean_up_thread()
            raise NotImplementedError("Not implemented yet")
