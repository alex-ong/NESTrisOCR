import Win32UICapture
from WindowMgr import WindowMgr
from PIL import Image
from fastocr import scoreImage
import time

def lerp(start, end, perc):
    return perc * (end-start) + start
    
def mult_rect(rect, mult):
    return (round(rect[2]*mult[0]+rect[0]),
            round(rect[3]*mult[1]+rect[1]),
            round(rect[2]*mult[2]),
            round(rect[3]*mult[3]))
            
CAPTURE_COORDS = (377,120,879,827)
scorePerc = (0.754,0.264,0.187,0.032)
linesPerc = (0.596,0.094,0.092,0.032)
SCORE_COORDS = mult_rect(CAPTURE_COORDS,scorePerc)
LINES_COORDS = mult_rect(CAPTURE_COORDS,linesPerc)

CALIBRATION = False
CALIBRATE_WINDOW = False
CALIBRATE_SCORE = False
CALIBRATE_LINES = True
WINDOW_NAME = "OBS"


def getWindow():
    wm = WindowMgr()    
    windows = wm.getWindows()    
    for window in windows:
        if window[1].startswith(WINDOW_NAME):
            return window[0]            
    return None

def calibrate():
    hwnd = getWindow()
    if hwnd is None:
        print ("Unable to find OBS window with title:",  WINDOW_NAME)
        return
    if CALIBRATE_WINDOW:
        img = Win32UICapture.ImageCapture(CAPTURE_COORDS,hwnd)
        img.show()
    if CALIBRATE_SCORE:
        img = Win32UICapture.ImageCapture(SCORE_COORDS,hwnd)
        img.show() 
    if CALIBRATE_LINES:
        img = Win32UICapture.ImageCapture(LINES_COORDS,hwnd)
        img.show() 
    return
        
def main():
    
    if CALIBRATION:
        calibrate()
        return
        
    while True:
        hwnd = getWindow()
        if hwnd:
            #img = Win32UICapture.ImageCapture(SCORE_COORDS,hwnd)
            #current = scoreImage(img,6)
            #print ("Score:", current)
            img = Win32UICapture.ImageCapture(LINES_COORDS,hwnd)
            
            current = scoreImage(img,3)
            print ("Lines:", current)
            
if __name__ == '__main__':
    main()
    

        