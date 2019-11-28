import cv2
import os
from PIL import Image
import time

from config import config


class WindowMgr():
    def checkWindow(self, ocv2_device_id):
        return True

    def getWindows(self):
        ocv2_device_id = int(config.WINDOW_NAME)

        return [[ocv2_device_id, config.WINDOW_NAME]]


class OpenCVMgr():
    def __init__(self):
        self.inputDevice = None
        self.imgBuf = None
        self.frameCount = 0

    def videoCheck(self, ocv2_device_id):
        if self.inputDevice is None:
            self.inputDevice = cv2.VideoCapture(ocv2_device_id)
            time.sleep(1)  # needed for Catalina, otherwise NextFrame would be black
            self.NextFrame()

    def ImageCapture(self, rectangle, ocv2_device_id):
        self.videoCheck(ocv2_device_id)

        return self.imgBuf.crop([
            rectangle[0],
            rectangle[1],
            rectangle[0] + rectangle[2],
            rectangle[1] + rectangle[3],
        ])

    def NextFrame(self):
        if self.inputDevice.isOpened():
            ret, cv2_im = self.inputDevice.read()
            if ret:
                cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
                self.imgBuf = Image.fromarray(cv2_im)
                self.frameCount += 1
                if self.frameCount % 1000 == 0:
                    print ('frames', self.frameCount)
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
