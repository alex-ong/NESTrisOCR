from config import config
import os
import cv2
from PIL import Image
import time


class WindowMgr:
    def __init__(self):
        pass

    def checkWindow(self, fileName):
        if os.path.exists(fileName):
            return True

    def getWindows(self):
        result = []
        for item in os.listdir("."):
            if item.lower().endswith("mp4"):
                result.append((item, item))

        return result


class FileMgr:
    def __init__(self):
        self.videoFile = None
        self.imgBuf = None
        self.frameRate = None
        self.frameCount = 0
        self.totalFrames = 1

    def videoCheck(self, fileName):
        if self.videoFile is None:
            self.videoFile = cv2.VideoCapture(fileName)
            self.frameRate = self.videoFile.get(cv2.CAP_PROP_FPS)
            self.totalFrames = int(self.videoFile.get(cv2.CAP_PROP_FRAME_COUNT))
            self.NextFrame()

    def ImageCapture(self, rectangle, fileName):
        self.videoCheck(fileName)
        return self.imgBuf.crop(
            [
                rectangle[0],
                rectangle[1],
                rectangle[0] + rectangle[2],
                rectangle[1] + rectangle[3],
            ]
        )

    def NextFrame(self):
        if self.videoFile.isOpened():
            ret, cv2_im = self.videoFile.read()
            if ret:
                cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
                self.imgBuf = Image.fromarray(cv2_im)
                self.frameCount += 1
                if self.frameCount % 1000 == 0:
                    print(
                        self.frameCount,
                        "{0:.2f}".format(self.frameCount * 100.0 / self.totalFrames)
                        + "% complete",
                    )
                return True

        return False

    def TimeStamp(self):
        if self.frameRate is not None:
            return self.frameCount * (1.0 / self.frameRate)
        return time.time()


def getWindow():
    wm = WindowMgr()

    windows = wm.getWindows()
    for window in windows:
        if window[1].startswith(config["calibration.source_id"]):
            return window[0]
    return None


imgCap = FileMgr()


def ImageCapture(rectangle, hwndTarget):
    global imgCap
    return imgCap.ImageCapture(rectangle, hwndTarget)


# returns false if we want to exit the program
def NextFrame():
    global imgCap
    return imgCap.NextFrame()


def TimeStamp():
    global imgCap
    return imgCap.TimeStamp()
