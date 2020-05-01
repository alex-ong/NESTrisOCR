from nestris_ocr.config import config
import platform

# decide which file capture method we are using.
if config["calibration.capture_method"] == "OPENCV":
    import nestris_ocr.capturing.opencv as WindowCapture
    from nestris_ocr.capturing.opencv import WindowMgr
elif config["calibration.capture_method"] == "FILE":
    import nestris_ocr.capturing.file as WindowCapture
    from nestris_ocr.capturing.file import WindowMgr
elif platform.system() == "Darwin":
    import nestris_ocr.capturing.quartz as WindowCapture
    from nestris_ocr.capturing.quartz_mgr import WindowMgr
else:
    import nestris_ocr.capturing.win32 as WindowCapture  # noqa: F401
    from nestris_ocr.capturing.win32_mgr import WindowMgr


def checkWindow(hwnd):
    wm = WindowMgr()
    # check for hwnd passed in as none too.
    return wm.checkWindow(hwnd) if hwnd else None


def getWindow():
    wm = WindowMgr()

    windows = wm.getWindows()
    for window in windows:
        if window[1].startswith(config["calibration.source_id"]):
            return window[0]
    return None


def lerp(start, end, perc):
    return perc * (end - start) + start


def mult_rect(rect, mult):
    return (
        round(rect[2] * mult[0]),
        round(rect[3] * mult[1]),
        round(rect[2] * mult[2]),
        round(rect[3] * mult[3]),
    )


def screenPercToPixels(w, h, rect_xywh):
    left = rect_xywh[0] * w
    top = rect_xywh[1] * h
    right = left + rect_xywh[2] * w
    bot = top + rect_xywh[3] * h
    return left, top, right, bot


def runFunc(func, args):
    return func(*args)


def tryGetInt(x):
    try:
        return True, round(float(x))
    except Exception:
        return False, 0


def tryGetFloat(x):
    try:
        return True, float(x)
    except Exception:
        return False, 0


def clamp(smol, big, value):
    if value < smol:
        return smol
    if value > big:
        return big
    return value
