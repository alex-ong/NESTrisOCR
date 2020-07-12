import time as pytime


ZERO_T = None


def time():
    return pytime.time() - ZERO_T


def sleep(ms):
    pytime.sleep(ms)


if ZERO_T is None:
    ZERO_T = pytime.time()
