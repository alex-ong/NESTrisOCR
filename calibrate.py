import nestris_ocr.calibration.calibrator as Calibrator
from nestris_ocr.config import config


def mainLoop():
    c = Calibrator.Calibrator(config)
    while not c.destroying:
        c.update()


if __name__ == "__main__":
    mainLoop()
