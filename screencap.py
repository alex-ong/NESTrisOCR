import Win32UICapture
from WindowMgr import WindowMgr
from PIL import Image, ImageDraw
from fastocr import scoreImage
from calibration import * #bad!
import time

def lerp(start, end, perc):
    return perc * (end-start) + start
    
def mult_rect(rect, mult):
    return (round(rect[2]*mult[0]+rect[0]),
            round(rect[3]*mult[1]+rect[1]),
            round(rect[2]*mult[2]),
            round(rect[3]*mult[3]))

def generate_stats(captureCoords, statBoxPerc, statHeight):    
    statGap = (statBoxPerc[3] - (7*statHeight))/6
    statGap = statGap + statHeight
    offsets = [i*(statGap) for i in range(7)]
    pieces = ['T','J','Z','O','S','L','I']
    result = {}
    for i, piece in enumerate(pieces):
        offset = offsets[i]
        box = (statBoxPerc[0],statBoxPerc[1]+offset,statBoxPerc[2],statHeight)
        result[piece] = mult_rect(captureCoords,box)
    return result

#the rate at which we process
FPS = 20
RATE = 0 #change this to 0 to go as fast as possible.
    
SCORE_COORDS = mult_rect(CAPTURE_COORDS,scorePerc)
LINES_COORDS = mult_rect(CAPTURE_COORDS,linesPerc)
LEVEL_COORDS = mult_rect(CAPTURE_COORDS,levelPerc)
STATS_COORDS = generate_stats(CAPTURE_COORDS,statsPerc,scorePerc[3])

CALIBRATION = False
CALIBRATE_WINDOW = True
CALIBRATE_SCORE = False
CALIBRATE_LINES = False
CALIBRATE_LEVEL = False
CALIBRATE_STATS = False



def getWindow():
    wm = WindowMgr()    
    windows = wm.getWindows()    
    for window in windows:
        if window[1].startswith(WINDOW_NAME):
            return window[0]            
    return None

def screenPercToPixels(w,h,rect_xywh):
    left = rect_xywh[0] * w
    top = rect_xywh[1] * h
    right = left + rect_xywh[2]*w
    bot = top+ rect_xywh[3]*h
    return (left,top,right,bot)
    
def highlight_calibration(img):    
    poly = Image.new('RGBA', (img.width,img.height))
    draw = ImageDraw.Draw(poly)
    #score
    red = (255,0,0,128)    
    blue = (0,0,255,128)
    draw.rectangle(screenPercToPixels(img.width,img.height,scorePerc),fill=red)
    #lines
    draw.rectangle(screenPercToPixels(img.width,img.height,linesPerc),fill=red)
    #level
    draw.rectangle(screenPercToPixels(img.width,img.height,levelPerc),fill=red)    
    #pieces
    draw.rectangle(screenPercToPixels(img.width,img.height,statsPerc),fill=blue)
    img.paste(poly,mask=poly)    
    del draw
    
def calibrate():
    hwnd = getWindow()
    if hwnd is None:
        print ("Unable to find OBS window with title:",  WINDOW_NAME)
        return
    if CALIBRATE_WINDOW:
        img = Win32UICapture.ImageCapture(CAPTURE_COORDS,hwnd)
        highlight_calibration(img)
        img.show()
    if CALIBRATE_SCORE:
        img = Win32UICapture.ImageCapture(SCORE_COORDS,hwnd)
        img.show() 
    if CALIBRATE_LINES:
        img = Win32UICapture.ImageCapture(LINES_COORDS,hwnd)
        img.show() 
    if CALIBRATE_LEVEL:
        img = Win32UICapture.ImageCapture(LEVEL_COORDS,hwnd)
        img.show()
    if CALIBRATE_STATS:
        for key in STATS_COORDS:
            img = Win32UICapture.ImageCapture(STATS_COORDS[key],hwnd)
            img.show()
    return
        
def main(onCap):
    import time
    if CALIBRATION:
        calibrate()
        return
        
    while True:
        t = time.time()
        hwnd = getWindow()
        result = {}
        if hwnd:            
            
            img = Win32UICapture.ImageCapture(SCORE_COORDS,hwnd)
            result["score"] = scoreImage(img,6)            
                        
            img = Win32UICapture.ImageCapture(LINES_COORDS,hwnd)            
            result["lines"] = scoreImage(img,3)
            
            img = Win32UICapture.ImageCapture(LEVEL_COORDS,hwnd)
            result["level"] = scoreImage(img,2)
            
            #todo: capture entire area and crop?
            for key in STATS_COORDS:
                img = Win32UICapture.ImageCapture(STATS_COORDS[key],hwnd)
                result[key] = scoreImage(img,3)
            
        toSleep = RATE - (time.time() - t)        
        if toSleep > 0:
            time.sleep(toSleep)
        onCap(result)
        
        
if __name__ == '__main__':
    main(print)
    

        