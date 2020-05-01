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
