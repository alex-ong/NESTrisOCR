import cv2
from collections import deque
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool

from PIL import Image
from typing import Tuple

from nestris_ocr.capturing.base import AbstractCapture
from nestris_ocr.utils import xywh_to_ltrb
from nestris_ocr.types import XYWHBox

FRAME_BUFFER = 150


class StreamCapture(AbstractCapture):
    def __init__(self, source_id: str, xywh_box: XYWHBox, extra_data: str) -> None:
        super().__init__(source_id, xywh_box, extra_data)

        print("Initializing stream URL", source_id)

        self.cap = cv2.VideoCapture(source_id)
        self.frame_buffer = deque([], FRAME_BUFFER)
        self.cv2_retval = None

        self.running = False
        self.read_lock = Lock()
        self.start()

    def get_image(self, rgb: bool = False) -> Tuple[float, Image.Image]:
        if not self.cv2_retval:
            raise Exception("Faulty capturing device")

        with self.read_lock:
            cv2_image = self.frame_buffer.popleft()

        if rgb:
            # can we do this in the thread pool?
            cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(cv2_image).crop(xywh_to_ltrb(self.xywh_box))

        return 0.0, image

    def start(self):
        if self.running:
            print("[!] Threaded video capturing has already been started.")
            return None
        self.running = True
        self.pool = ThreadPool(processes=1)
        self.pool.apply_async(self.update)

    def update(self):
        while self.running:
            cv2_retval, cv2_image = self.cap.read()
            self.inject_image(cv2_retval, cv2_image)

        self.cap.release()

    def inject_image(self, cv2_retval, image):
        with self.read_lock:
            self.cv2_retval = cv2_retval
            self.frame_buffer.append(image)

    def stop(self):
        self.running = False
        self.pool.terminate()
        self.pool.join()

    def fast_restart(self) -> bool:
        return False
