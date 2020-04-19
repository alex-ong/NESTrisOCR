import cv2
import os
from PIL import Image
from gamecap.deinterlacer import deinterlace, InterlaceMode, InterlaceRes
import time

from config import config


class WindowMgr:
    def checkWindow(self, ocv2_device_id):
        return True

    def getWindows(self):
        # we keep cv2_device_id as string for now, so it is always truthy
        # If we cast to int now, device id 0 will not be truthy and can't be used
        ocv2_device_id = config.WINDOW_NAME

        return [[ocv2_device_id, config.WINDOW_NAME]]


INTERLACE_MODE = InterlaceMode.BOTTOM_FIRST
INTERLACE_RES = InterlaceRes.HALF


class OpenCVMgr:
    def __init__(self):
        self.inputDevice = None
        self.imgBuf = None
        self.nextImgBuf = None  # used for 30i->60p
        self.lastBuf = 0
        self.frameCount = 0

    def videoCheck(self, ocv2_device_id):
        if self.inputDevice is None:
            try:
                # OpenCV support local device IDs AND stream URLs
                # Let's do a blind cast attempt to int
                #  - if it can cast, we get a local device ID
                #  - if it cannot cast, we assume we have a stream URL and use it as is
                ocv2_device_id = int(ocv2_device_id)
            except:
                pass

            self.inputDevice = cv2.VideoCapture(ocv2_device_id)
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
        if self.inputDevice.isOpened():
            # if we are doubling framecount, access second frame here.
            if self.nextImgBuf:
                self.imgBuf = self.nextImgBuf
                self.nextImgBuf = None
                self.frameCount += 1
                return True

            # do the actual read from the device. Note that this is blocking.
            ret, cv2_im = self.inputDevice.read()
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
