from nestris_ocr.calibration.calibrator import Calibrator
from nestris_ocr.config import config
from nestris_ocr.capturing import uncached_capture


def mainLoop():
    c = Calibrator(config)
    while not c.destroying:
        c.update()
    uncached_capture().stop()


if __name__ == "__main__":
    mainLoop()
