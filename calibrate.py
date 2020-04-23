from nestris_ocr.calibration.calibrator import Calibrator
from nestris_ocr.config import config


def mainLoop():
    c = Calibrator(config)
    while not c.destroying:
        c.update()


if __name__ == "__main__":
    mainLoop()
