import time
import threading

import cv2
from PIL import Image

from nestris_ocr.capturing.deinterlacer import deinterlace, InterlaceMode, InterlaceRes
from nestris_ocr.config import config


class WindowMgr:
    def checkWindow(self, ocv2_device_id):
        return True

    def getWindows(self):
        # we keep cv2_device_id as string for now, so it is always truthy
        # If we cast to int now, device id 0 will not be truthy and can't be used
        ocv2_device_id = config["calibration.source_id"]

        return [[ocv2_device_id, config["calibration.source_id"]]]


INTERLACE_MODE = InterlaceMode.BOTTOM_FIRST
INTERLACE_RES = InterlaceRes.HALF


class VideoCaptureThreading:
    def __init__(self, src=0, width=640, height=480):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print("[!] Threaded video capturing has already been started.")
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()


class OpenCVMgr:
    def __init__(self):
        self.cap = None
        self.imgBuf = None
        self.nextImgBuf = None  # used for 30i->60p
        self.lastBuf = 0
        self.frameCount = 0

    def videoCheck(self, ocv2_device_id):
        if not self.cap:
            try:
                # OpenCV support local device IDs AND stream URLs
                # Let's do a blind cast attempt to int
                #  - if it can cast, we get a local device ID
                #  - if it cannot cast, we assume we have a stream URL and use it as is
                ocv2_device_id = int(ocv2_device_id)
            except Exception:
                pass

            self.cap = VideoCaptureThreading(ocv2_device_id)
            self.cap.start()

            time.sleep(1)  # Need to wait a second for the input device to initialize

    def ImageCapture(self, rectangle, ocv2_device_id):
        self.videoCheck(ocv2_device_id)

        # most of the time NextFrame() is manually called from outside, before ImageCapture()
        # when NextFrame() is not called, we would try to reply with fresh enough image capture
        if time.time() - self.lastBuf > 0.3:
            self.NextFrame()

        return self.imgBuf.crop(
            [
                rectangle[0],
                rectangle[1],
                rectangle[0] + rectangle[2],
                rectangle[1] + rectangle[3],
            ]
        )

    def NextFrame(self):
        if self.cap.started:
            # if we are doubling framecount, access second frame here.
            if self.nextImgBuf:
                self.imgBuf = self.nextImgBuf
                self.nextImgBuf = None
                self.frameCount += 1
                return True

            # non-blockingly getting the latest cached read from the device
            ret, cv2_im = self.cap.read()
            if ret:
                cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
                im = Image.fromarray(cv2_im)
                images = deinterlace(im, INTERLACE_MODE, INTERLACE_RES)
                self.imgBuf = images[0]
                self.nextImgBuf = images[1]
                self.lastBuf = time.time()
                self.frameCount += 1
                if self.frameCount % 1000 == 0:
                    print("frames", self.frameCount)
                return True

        return False


imgCap = OpenCVMgr()


def ImageCapture(rectangle, hwndTarget):
    global imgCap
    return imgCap.ImageCapture(rectangle, hwndTarget)


def NextFrame():
    # returns false if we want to exit the program
    global imgCap
    return imgCap.NextFrame()
