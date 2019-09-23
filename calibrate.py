import calibration.Calibrator as Calibrator
from config import config

    
if __name__ == '__main__':
    c = Calibrator.Calibrator(config)
    img = Calibrator.draw_calibration(config)
    img.show()