import calibration.Calibrator as Calibrator
from config import config

    
if __name__ == '__main__':	
    c = Calibrator.Calibrator(config)    
    while not c.destroying:
        c.update()