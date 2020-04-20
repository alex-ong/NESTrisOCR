from config import config
import platform

# decide which file capture method we are using.
if config.get("calibration.capture_method") == "OPENCV":
    import gamecap.opencv as WindowCapture
    from gamecap.opencv import WindowMgr
elif config.get("calibration.capture_method") == "FILE":
    import gamecap.file as WindowCapture
    from gamecap.file import WindowMgr
elif platform.system() == "Darwin":
    import gamecap.quartz as WindowCapture
    from gamecap.quartz_mgr import WindowMgr
else:
    import gamecap.win32 as WindowCapture  # noqa: F401
    from gamecap.win32_mgr import WindowMgr


def checkWindow(hwnd):
    wm = WindowMgr()
    # check for hwnd passed in as none too.
    return wm.checkWindow(hwnd) if hwnd else None


def getWindow():
    wm = WindowMgr()

    windows = wm.getWindows()
    for window in windows:
        if window[1].startswith(config.get("calibration.source_id")):
            return window[0]
    return None


def lerp(start, end, perc):
    return perc * (end - start) + start


def mult_rect(rect, mult):
    return (
        round(rect[2] * mult[0] + rect[0]),
        round(rect[3] * mult[1] + rect[1]),
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


FIRST = True


# runs a bunch of tasks given a pool. Supports singleThread.
def runTasks(pool, rawTasks):
    global FIRST

    result = {}
    if pool:  # multithread
        tasks = []
        for task in rawTasks:
            tasks.append(pool.apply_async(task[0], task[1]))

        taskResults = [(res.get() if FIRST else res.get(5.0)) for res in tasks]
        FIRST = False
        for key, number in taskResults:
            result[key] = number

    else:  # single thread
        for task in rawTasks:
            key, number = runFunc(task[0], task[1])
            result[key] = number

    return result


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


# coords is supplied in XYWH format
def XYWHOffsetAndConvertToLTBR(offset, coords):
    return (
        coords[0] - offset[0],
        coords[1] - offset[1],
        coords[0] - offset[0] + coords[2],
        coords[1] - offset[1] + coords[3],
    )
