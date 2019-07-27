import platform

if platform.system() == 'Darwin':
    import QuartzCapture as WindowCapture
    from QuartzWindowMgr import WindowMgr

else:
    import Win32UICapture as WindowCapture
    from Win32WindowMgr import WindowMgr

from PIL import Image, ImageDraw
from fastocr import scoreImage
from calibration import * #bad!
from multiprocessing import Pool
from Networking import TCPClient
import json
import time

def lerp(start, end, perc):
    return perc * (end-start) + start
    
def mult_rect(rect, mult):
    return (round(rect[2]*mult[0]+rect[0]),
            round(rect[3]*mult[1]+rect[1]),
            round(rect[2]*mult[2]),
            round(rect[3]*mult[3]))

def generate_stats(captureCoords, statBoxPerc, statHeight, do_mult=True):    
    statGap = (statBoxPerc[3] - (7*statHeight))/6
    statGap = statGap + statHeight
    offsets = [i*(statGap) for i in range(7)]
    pieces = ['T','J','Z','O','S','L','I']
    result = {}
    for i, piece in enumerate(pieces):
        offset = offsets[i]
        box = (statBoxPerc[0],statBoxPerc[1]+offset,statBoxPerc[2],statHeight)
        if do_mult:
            result[piece] = mult_rect(captureCoords,box)
        else:
            result[piece] = box
    return result

#patterns for digits. 
#A = 0->9 + A->F, 
#D = 0->9
SCORE_PATTERN = 'ADDDDD'
LINES_PATTERN = 'DDD'
LEVEL_PATTERN = 'AA'
STATS_PATTERN = 'DDD'

SCORE_COORDS = mult_rect(CAPTURE_COORDS,scorePerc)
LINES_COORDS = mult_rect(CAPTURE_COORDS,linesPerc)
LEVEL_COORDS = mult_rect(CAPTURE_COORDS,levelPerc)

#piece stats.
STATS_COORDS  = generate_stats(CAPTURE_COORDS,statsPerc,scorePerc[3])
STATS2_COORDS = mult_rect(CAPTURE_COORDS, stats2Perc)
STATS_METHOD  = 'TEXT' #can be TEXT or FIELD. Field isn't implmeented yet, so just use TEXT.
STATS_ENABLE  = True


CALIBRATION = False
CALIBRATE_WINDOW = True
CALIBRATE_SCORE = False
CALIBRATE_LINES = False
CALIBRATE_LEVEL = False
CALIBRATE_STATS = False
MULTI_THREAD = 1
RATE = 0.064

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
    orange = (255,165,0,128)
    draw.rectangle(screenPercToPixels(img.width,img.height,scorePerc),fill=red)
    #lines
    draw.rectangle(screenPercToPixels(img.width,img.height,linesPerc),fill=red)
    #level
    draw.rectangle(screenPercToPixels(img.width,img.height,levelPerc),fill=red)    
    if STATS_METHOD == 'TEXT':
        #pieces
        draw.rectangle(screenPercToPixels(img.width,img.height,statsPerc),fill=blue)
        for value in generate_stats(CAPTURE_COORDS,statsPerc,scorePerc[3],False).values():
            draw.rectangle(screenPercToPixels(img.width,img.height,value),fill=orange)
    else: #STATS_METHOD == 'FIELD':
        draw.rectangle(screenPercToPixels(img.width,img.height,stats2Perc),fill=blue)
        
    img.paste(poly,mask=poly)    
    del draw
    
def calibrate():
    hwnd = getWindow()
    if hwnd is None:
        print ("Unable to find OBS window with title:",  WINDOW_NAME)
        return
    if CALIBRATE_WINDOW:
        img = WindowCapture.ImageCapture(CAPTURE_COORDS,hwnd)
        highlight_calibration(img)
        img.show()
    if CALIBRATE_SCORE:
        img = WindowCapture.ImageCapture(SCORE_COORDS,hwnd)
        img.show() 
    if CALIBRATE_LINES:
        img = WindowCapture.ImageCapture(LINES_COORDS,hwnd)
        img.show() 
    if CALIBRATE_LEVEL:
        img = WindowCapture.ImageCapture(LEVEL_COORDS,hwnd)
        img.show()
    if CALIBRATE_STATS:
        for key in STATS_COORDS:
            img = WindowCapture.ImageCapture(STATS_COORDS[key],hwnd)
            img.show()
    return

def captureAndOCR(coords,hwnd,digitPattern,taskName,draw=False,red=False):
    img = WindowCapture.ImageCapture(coords,hwnd)
    return taskName, scoreImage(img,digitPattern,draw,red)

#this is a stub. Don't use it!
def captureAndOCRBoard(coords, hwnd):
    img = WindowCapture.ImageCapture(coords, hwnd)
    return None

def runFunc(func, args):
    return func(*args)
    
def main(onCap):
    import time
    if CALIBRATION:
        calibrate()
        return
    
    if MULTI_THREAD >= 2:
        p = Pool(MULTI_THREAD)
    else:
        p = None
    
    while True:
        t = time.time()
        hwnd = getWindow()
        result = {}
        if hwnd:       
            rawTasks = []
            rawTasks.append((captureAndOCR,(SCORE_COORDS,hwnd,SCORE_PATTERN,"score")))
            rawTasks.append((captureAndOCR,(LINES_COORDS,hwnd,LINES_PATTERN,"lines")))
            rawTasks.append((captureAndOCR,(LEVEL_COORDS,hwnd,LEVEL_PATTERN,"level")))
            
            if STATS_ENABLE:
                if STATS_METHOD == 'TEXT':
                    for key in STATS_COORDS:
                        rawTasks.append((captureAndOCR,(STATS_COORDS[key],hwnd,STATS_PATTERN,key,False,True)))
                else: #if STATS_METHOD == 'FIELD'
                    rawTasks.append((captureAndOCRBoard, (STATS2_COORDS, hwnd)))
                
            result = {}
            if p: #multithread
                tasks = []
                for task in rawTasks:
                    tasks.append(p.apply_async(task[0],task[1]))                
                taskResults = [res.get(timeout=1) for res in tasks]
                for key, number in taskResults:
                    result[key] = number
                
            else: #single thread                   
                for task in rawTasks:
                    key, number = runFunc(task[0],task[1])
                    result[key] = number
        
            onCap(result)  
        while time.time() < t + RATE:
            time.sleep(0.001)
        
class CachedSender(object):
    def __init__(self, client):
        self.client = client
        self.lastMessage = None

    #convert message to jsonstr and then send if its new.
    def sendResult(self, message):
        print(message)
        jsonMessage = json.dumps(message,indent=2)        
        self.client.sendMessage(jsonMessage)

    
def sendResult(client, message):    
    jsonStr = json.dumps(message, indent=2)
    client.sendMessage(jsonStr)
        
if __name__ == '__main__':
    client = TCPClient.CreateClient('127.0.0.1',3338)
    cachedSender = CachedSender(client)
    main(cachedSender.sendResult)
    

        