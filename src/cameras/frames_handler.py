import copy
import logging
import numpy as np
from queue import Queue
from vmbpy import Camera, Frame, Stream, FrameStatus
from PySide6.QtCore import QThread, QMutex
from src.cameras.handling_elements.basic_handler import BasicHandler
from src.utils.qt.thread_event import ThreadEvent

logger = logging.getLogger("cameras")


class FramesHandler(QThread):
    FRAME_QUEUE_SIZE = 10

    def __init__(self, camera: Camera, frame_queue_size: int = 10) -> None:
        super().__init__()
        self._frame_queue = Queue(frame_queue_size)
        self._camera = camera
        self._name = self._camera.get_id()  # camera name
        self._handlers: list[BasicHandler] = []
        self._handler_mutex = QMutex()
        self._stop_thread = ThreadEvent()

    def __del__(self) -> None:
        logger.info(f"Deleting thread for cam {self._name}")
        self.quit()

    def register_handler(self, handler: BasicHandler) -> bool:
        if not self._handler_mutex.tryLock(1000):
            logger.error(
                f"Camera {self._name}: Unable to lock mutex for handler reqistration"
            )
            return False

        self._handlers.append(handler)
        self._handler_mutex.unlock()

        return True

    def unregister_handler(self, handler: BasicHandler) -> bool:
        if not self._handler_mutex.tryLock(1000):
            logger.error(
                f"Camera {self._name}: Unable to lock mutex for handler reqistration"
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

    def on_frame(self, camera: Camera, stream: Stream, frame: Frame):
        if frame.get_status() == FrameStatus.Complete:
            if not self._frame_queue.full():
                frame_cpy = copy.deepcopy(frame)
                # we checked that frame is not full before, so
                # we do not have to handle is full exception
                self._frame_queue.put_nowait(frame_cpy.as_numpy_ndarray())
            else:
                logger.warning(f"Cam {self._name} is full")

        camera.queue_frame(frame)

    def _frame_available(self) -> bool:
        return not self._frame_queue.empty()

    def _get_the_newest_frame(self) -> np.ndarray | None:
        frames_on_queue = self._frame_queue.qsize()

        if frames_on_queue == 0:
            return None

        if frames_on_queue > 1:
            logger.warn(
                f"Camera {self._name} thread is delayed"
                f" about {frames_on_queue - 1} frames"
            )

        while frames_on_queue > 0:
            # we checked empty before, no need to handle exception
            frame = self._frame_queue.get_nowait()
            frames_on_queue -= 1

        return frame

    def _add_frame_to_handlers(self, frame: np.array) -> None:
        if frame is None:
            logger.warn(f"Camera {self._name}, frame is None :C")
            return

        for handler in self._handlers:
            handler.add_frame(frame)

    def set_mako(self):
        feat = self._camera.get_feature_by_name('Height')
        feat.set(1000)

        feat = self._camera.get_feature_by_name('Width')
        feat.set(2000)
        
        feat = self._camera.get_feature_by_name('OffsetX')
        feat.set(0)

        feat = self._camera.get_feature_by_name('OffsetY')
        feat.set(0)

        feature = self._camera.get_feature_by_name('AcquisitionFrameRateAbs')
        feature.set(20) #specifies 30FPS
        # set the other features TriggerSelector and TriggerMode
        feature = self._camera.get_feature_by_name("TriggerSelector")
        feature.set("FrameStart")
        feature = self._camera.get_feature_by_name("TriggerMode")
        feature.set("Off")

    def set_alvium(self):
        feat = self._camera.get_feature_by_name('Height')
        feat.set(1000)

        feat = self._camera.get_feature_by_name('Width')
        feat.set(2000)
        
        feat = self._camera.get_feature_by_name('OffsetX')
        feat.set(2000)

        feat = self._camera.get_feature_by_name('OffsetY')
        feat.set(1000)

        feature = self._camera.get_feature_by_name('AcquisitionFrameRateEnable')
        feature.set(True)

        feature = self._camera.get_feature_by_name('AcquisitionFrameRate')
        feature.set(7)

    def run(self) -> None:
        logger.info(f"Frame handler thread started for camera {self._name}")

        alive = True
        with self._camera:
            print(self._camera.get_model())
            if "Mako" in self._camera.get_model():
                self.set_mako()
            else:
                self.set_alvium()
            
            self._camera.start_streaming(self.on_frame)
            while alive:
                if self._frame_available():
                    frame = self._get_the_newest_frame()
                    try:
                        self._handler_mutex.lock()
                        self._add_frame_to_handlers(frame)
                    finally:
                        self._handler_mutex.unlock()

                if self._stop_thread.happens():
                    alive = False

            self._camera.stop_streaming()

    def _clean_up(self):
        self._stop_thread.restart()

        while not self._frame_queue.empty:
            self._frame_queue.get_nowait()

    def quit(self) -> None:
        logger.info(f"Wainting for frame handler to stop for camera {self._name}")
        self._stop_thread.set()
        super().wait()

        logger.info(f"Frame handler thread stopped for camera {self._name}")
        self._clean_up()


    @property
    def name(self) -> str:
        return self._name
