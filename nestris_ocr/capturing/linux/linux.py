import Xlib
import Xlib.display
from Xlib import X
from PIL import Image


class LinuxUICapture(object):
    def __init__(self):
        self.last_hwnd = None
        self.cached_win = None

    def ImageCapture(self, rectangle, hwnd):
        x, y, w, h = rectangle
        if w <= 0 or h <= 0 or hwnd == 0 or hwnd is None:
            return None

        if self.last_hwnd != hwnd:
            self.last_hwnd = hwnd
            self.cached_win = None

        if self.cached_win is None:
            display = Xlib.display.Display()
            self.cached_win = display.create_resource_object("window", hwnd)

        try:
            geom = self.cached_win.get_geometry()
        except Exception:  # Xlib.error.BadDrawable
            raise

        x, y, w, h = self.check_geometry(geom, (x, y, w, h))

        try:
            raw = self.cached_win.get_image(x, y, w, h, X.ZPixmap, 0xFFFFFFFF)
        except Xlib.error.BadMatch:
            raise

        # note that we actually want to support a BGR and RGB Image
        # for the return type eventually, since BGR is double the speed
        # this isn't implemented in windows yet either.

        # if useRGB:
        return Image.frombytes("RGB", (w, h), raw.data, "raw", "BGRX")
        # else:
        # return Image.frombytes("BGR", (w, h), raw.data, "raw", "BGRX")

    def check_geometry(self, geom, rectangle):
        x, y, w, h = rectangle
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > geom.width:
            x = geom.width - 1
        if y > geom.height:
            y = geom.height - 1
        if x + w > geom.width:
            w = geom.width - x
        if y + h > geom.height:
            h = geom.height - h
        return (x, y, w, h)


# I believe that we no longer need the below items - Alex
imgCap = LinuxUICapture()


def ImageCapture(rectangle, hwnd):
    global imgCap
    return imgCap.ImageCapture(rectangle, hwnd)


def NextFrame():
    global imgCap
    return True
