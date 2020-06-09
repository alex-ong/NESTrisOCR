import cv2
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool

from PIL import Image
import time
import platform
from typing import Tuple

from nestris_ocr.capturing.base import AbstractCapture
from nestris_ocr.utils import xywh_to_ltrb
from nestris_ocr.types import XYWHBox
from nestris_ocr.capturing.opencv.list_devices import get_device_list

WINDOWS_BACKENDS = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_VFW]


class OpenCVCapture(AbstractCapture):
    def __init__(self, source_id: str, xywh_box: XYWHBox, extra_data: str) -> None:
        super().__init__(source_id, xywh_box, extra_data)
        print("Initializing capture device")
        source_id = self.clean_source_id()
        if platform.system() == "Windows":
            backend = self.get_backend(source_id)
            self.cap = cv2.VideoCapture(source_id, backend)
            # todo: call benchmark_setup and cache result in config?
        else:
            self.cap = cv2.VideoCapture(source_id)
        self.cv2_retval = None
        self.cv2_image = None
        self.image_ts = None

        self.running = False
        self.read_lock = Lock()
        self.start()

    def clean_source_id(self) -> int:
        try:
            return int(self.source_id)
        except ValueError:
            return 0

    def get_backend(self, source_id: int) -> int:
        # check cache:
        devices = get_device_list()
        if self.extra_data:
            cached_source_id, device_name, backend = self.extra_data.split("|")
            if int(cached_source_id) == source_id:
                try:
                    if devices[source_id] == device_name:
                        print("Loading", device_name, "with backend:", backend)
                        return int(backend)
                except IndexError:
                    pass

        if source_id not in devices:
            return cv2.CAP_ANY

        # lets benchmark, and then store result.
        device_name = devices[source_id]
        print("Benchmarking OpenCV backends for:", device_name)
        runtime, backend = self.benchmark_backends(source_id, WINDOWS_BACKENDS)
        print("Fastest backend:", backend, " Startup time: ", runtime)
        self.extra_data = "|".join([str(source_id), device_name, str(backend)])
        return backend

    def benchmark_backends(self, source_id, backends):
        times = []

        for backend in backends:
            timer = time.time()
            try:
                cap = cv2.VideoCapture(int(source_id), backend)
                cap.release()
            except:  # noqa  E722
                pass  # if the capture method is invalid, *sometimes* it crashes
            else:
                t = time.time() - timer
                if t > 0.05:  # invalid caputre loads instantly.
                    times.append((time.time() - timer, backend))

        times.sort(key=lambda x: x[0])
        return times[0]

    def get_image(self, rgb: bool = False) -> Tuple[float, Image.Image]:
        if not self.cv2_retval:
            raise Exception("Faulty capturing device")

        with self.read_lock:
            cv2_image = self.cv2_image.copy()
            image_ts = self.image_ts

        if rgb:
            cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(cv2_image).crop(xywh_to_ltrb(self.xywh_box))

        return image_ts, image

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
            with self.read_lock:
                self.cv2_retval = cv2_retval
                self.cv2_image = cv2_image
                self.image_ts = time.time()
        self.cap.release()

    def stop(self):
        self.running = False
        self.pool.terminate()
        self.pool.join()
