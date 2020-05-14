import Xlib
import Xlib.display
from Xlib import X
from PIL import Image


class LinuxUICapture(object):
    def __init__(self):
        self.lastRectangle = None
        self.lastHwnd = None

    def ImageCapture(self, rectangle, hwnd):
        x, y, w, h = rectangle
        if w <= 0 or h <= 0 or hwnd == 0:
            raise
        # at some point we want to cache the root/win
        # root = Xlib.display.Display().screen().root
        win = Xlib.display.Display().create_resource_object("window", hwnd)

        # we also want to retry on failure, or at least return blank frame
        try:
            geom = win.get_geometry()
        except Exception:  # Xlib.error.BadDrawable
            raise
        if w > geom.width:
            w = geom.width
        if h > geom.height:
            h = geom.height

        try:
            raw = win.get_image(x, y, w, h, X.ZPixmap, 0xFFFFFFFF)
        except Xlib.error.BadMatch:
            raise
        # note that we actually want to support a BGR and RGB Image
        # for the return type eventually, since BGR is double the speed
        im = Image.frombytes("RGB", (w, h), raw.data, "raw", "BGRX")
        if self.lastRectangle != rectangle:
            self.lastRectangle = rectangle
        if self.lastHwnd != hwnd:
            self.lastHwnd = hwnd
        return im


# I believe that we no longer need the below items - Alex
imgCap = LinuxUICapture()


def ImageCapture(rectangle, hwnd):
    global imgCap
    return imgCap.ImageCapture(rectangle, hwnd)


def NextFrame():
    global imgCap
    return True
