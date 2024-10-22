import copy
import logging
import numpy as np
import numpy.typing as npt
from typing import override
from queue import Queue
from vmbpy import Camera, Frame, Stream, FrameStatus, PersistType, PixelFormat
from PySide6.QtCore import QThread, QMutex, Slot, Qt, Signal
from src.cameras.frame_handlers.basic_frame_handler import BasicFrameHandler
from src.utils.qt.thread_event import ThreadEvent
import traceback

logger = logging.getLogger("cameras")


class CameraHandler(QThread):
    FRAME_QUEUE_SIZE = 1
    error = Signal(str)

    def __init__(
        self,
        camera: Camera,
    ) -> None:
        """Constructor

        Args:
            camera (Camera): Reference to the VmbCamera object
        """
        super().__init__()
        self._camera = camera
        self._id = self._camera.get_id()  # camera name

        self._frame_queue = Queue(self.FRAME_QUEUE_SIZE)
        self._handlers: list[BasicFrameHandler] = []
        self._handler_mutex = QMutex()
        self._stop_signal = ThreadEvent()
        self._streaming = ThreadEvent()
        self._config_file = None  # camera config file, None means no config file

    @Slot()
    def on_handler_started(self):
        """Handler started slot"""
        self.start_streaming()

    @Slot()
    def on_handler_stopped(self):
        """Handler stopped slot"""
        self.stop_streaming()

    def register_frame_handler(self, handler: BasicFrameHandler) -> bool:
        """Register a frame handler to the camera

        Args:
            handler (BasicFrameHandler): The handler to be registered

        Returns:
            bool: True if the handler was registered successfully, False otherwise
        """
        logger.info(f"Registering handler {handler} for camera {self._id}")

        if not self._handler_mutex.tryLock(1000):
            logger.error(
                f"Camera {self._id}: Unable to lock mutex for handler reqistration"
            )
            return False

        self._handlers.append(handler)
        # Connect handler signals, to inform the camera handler thread
        # that the handler has started or stopped and request to start/stop
        # streaming (start/stop the camera handler thread)
        handler.started.connect(
            self.on_handler_started, Qt.ConnectionType.DirectConnection
        )
        handler.stopped.connect(
            self.on_handler_stopped, Qt.ConnectionType.DirectConnection
        )

        self._handler_mutex.unlock()

        return True

    def unregister_frame_handler(self, handler: BasicFrameHandler) -> bool:
        """Unregister a frame handler from the camera

        Args:
            handler (BasicFrameHandler): The handler to be unregistered

        Returns:
            bool: True if the handler was unregistered successfully, False otherwise
        """
        if not self._handler_mutex.tryLock(1000):
            logger.error(
                f"Camera {self._id}: Unable to lock mutex for handler reqistration"
            )
            return False

        if handler not in self._handlers:
            self._handler_mutex.unlock()
            logger.error("Unknown handler")
            return False

        handler.stop()
        self._handlers.remove(handler)

        self._handler_mutex.unlock()

        return True

    def set_config_file(self, config_file: str) -> None:
        """Set the camera config file that will be loaded when
        the camera handler thread starts
        """
        self._config_file = config_file

    def _on_frame(self, camera: Camera, stream: Stream, frame: Frame):
        """Frame callback function

        Args:
            camera (Camera): camera object
            stream (Stream): stream object
            frame (Frame): frame
        """
        if frame.get_status() == FrameStatus.Complete:
            frame_cpy = copy.deepcopy(frame)

            if self._frame_queue.full():
                self._frame_queue.get_nowait()
                logger.warning(f"Camera {self._id} lost one frame")

            debayered_frame = frame_cpy.convert_pixel_format(PixelFormat.Rgb8)
            self._frame_queue.put_nowait(debayered_frame.as_numpy_ndarray())

        camera.queue_frame(frame)

    def _frame_available(self) -> bool:
        """Check if there is a frame available in the queue

        Returns:
            bool: True if there is a frame available, False otherwise
        """
        return not self._frame_queue.empty()

    def _get_the_newest_frame(self) -> np.ndarray | None:
        """Get the newest frame from the queue
        This methode also removes all the other frames from the queue
        """
        frames_on_queue = self._frame_queue.qsize()

        if frames_on_queue == 0:
            return None

        # if frames_on_queue > 1:
        #     logger.warn(
        #         f"Camera {self._id} thread is delayed"
        #     )

        # while frames_on_queue > 0:
        #     # we checked empty before, no need to handle exception
        #     frame = self._frame_queue.get_nowait()
        #     frames_on_queue -= 1
        frame = self._frame_queue.get_nowait()

        return frame

    def _add_frame_to_handlers(self, frame: npt.ArrayLike) -> None:
        """Add the frame to all the registered handlers

        Args:
            frame (npt.ArrayLike): The frame to be added
        """
        if frame is None:
            logger.warning(f"Camera {self._id}, frame is None :C")
            return

        for handler in self._handlers:
            handler.add_frame(frame)

    def _handle_frames(self):
        """Handle the frames that are available in the queue"""
        if not self._frame_available():
            return

        if not self._handler_mutex.tryLock(1000):
            logger.error(f"Camera {self._id}: Unable to lock mutex for frame handling")
            return

        try:
            frame = self._get_the_newest_frame()

            self._add_frame_to_handlers(frame)
        finally:
            self._handler_mutex.unlock()

    def _handle_config_file(self) -> None:
        """Handle the camera config file update"""
        if self._config_file:
            self._camera.stop_streaming()

            self._config_file = None

            self._camera.start_streaming(self._on_frame)

    def _handle_exception(self, e: Exception) -> None:
        """Handle the exception

        Args:
            e (Exception): The exception to be handled
        """
        message = f"Error in camera {self._id}: {e}"
        logger.error(message)
        self.error.emit(message)

    def _thread_loop(self) -> None:
        """Thread main loop"""
        while not self._stop_signal.occurs():
            self._handle_frames()
            self._handle_config_file()

    def _clean_up(self):
        """Clean up the camera handler thread"""
        while not self._frame_queue.empty():
            self._frame_queue.get_nowait()

        logger.info(f"Frame handler thread stopped for camera {self._id}")

    def start_streaming(self):
        """Start the camera streaming"""
        self._streaming.set()

    def stop_streaming(self):
        """Stop the camera streaming"""
        if all(handler.is_running for handler in self._handlers):
            self._streaming.clear()

    @override
    def run(self) -> None:
        """Thread main loop"""
        logger.info(f"Frame handler thread started for camera {self._id}")
        self._stop_signal.clear()

        with self._camera:
            self._camera.load_settings(self._config_file, PersistType.NoLUT)

            while not self._stop_signal.occurs():
                try:
                    if self._streaming.occurs() and not self._camera.is_streaming():
                        self._camera.start_streaming(self._on_frame)

                    if not self._streaming.occurs() and self._camera.is_streaming():
                        self._camera.stop_streaming()

                    self._handle_frames()
                except Exception as e:
                    print(traceback.print_exc())
                    self._handle_exception(e)

        self._clean_up()

    @override
    def quit(self) -> None:
        """Stops the camera handler thread"""
        logger.info(f"Waiting for frame handler to stop for camera {self._id}")

        if self._stop_signal.occurs():
            return

        self._stop_signal.set()
        super().wait()

        for handler in self._handlers:
            handler.stop()

    @property
    def id(self) -> str:
        return self._id
