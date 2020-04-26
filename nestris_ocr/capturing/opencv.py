import cv2
from PIL import Image
import time
import threading

from nestris_ocr.capturing.base import AbstractCapture


class OpenCVCapture(AbstractCapture):
    def __init__(self, source_id):
        super().__init__(source_id)

        self.cap = cv2.VideoCapture(int(source_id))

        self.cv2_retval = None
        self.cv2_image = None
        self.image_ts = None

        self.started = False
        self.read_lock = threading.Lock()
        self.start()

    def get_image(self) -> (int, Image):
        with self.read_lock:
            cv2_retval = self.cv2_retval
            cv2_image = self.cv2_image.copy()
            image_ts = self.image_ts

        if not cv2_retval:
            raise Exception("Faulty capturing device")

        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(cv2_image)

        return image_ts, image

    def start(self):
        if self.started:
            print("[!] Threaded video capturing has already been started.")
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()

    def update(self):
        while self.started:
            cv2_retval, cv2_image = self.cap.read()
            with self.read_lock:
                self.cv2_retval = cv2_retval
                self.cv2_image = cv2_image
                self.image_ts = time.time()

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()
