import Win32UICapture
from WindowMgr import WindowMgr
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
    
SCORE_COORDS = mult_rect(CAPTURE_COORDS,scorePerc)
LINES_COORDS = mult_rect(CAPTURE_COORDS,linesPerc)
LEVEL_COORDS = mult_rect(CAPTURE_COORDS,levelPerc)
STATS_COORDS = generate_stats(CAPTURE_COORDS,statsPerc,scorePerc[3])

CALIBRATION = False
CALIBRATE_WINDOW = False
CALIBRATE_SCORE = False
CALIBRATE_LINES = False
CALIBRATE_LEVEL = False
CALIBRATE_STATS = False
MULTI_THREAD = 8


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

def captureAndOCR(coords,hwnd,digits,taskName):
    img = Win32UICapture.ImageCapture(coords,hwnd)
    return taskName, scoreImage(img,digits)

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
            rawTasks.append((captureAndOCR,(SCORE_COORDS,hwnd,6,"score")))
            rawTasks.append((captureAndOCR,(LINES_COORDS,hwnd,3,"lines")))
            rawTasks.append((captureAndOCR,(LEVEL_COORDS,hwnd,2,"level")))
            for key in STATS_COORDS:
                rawTasks.append((captureAndOCR,(STATS_COORDS[key],hwnd,3,key)))
                
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
        #print (time.time() - t)
        
class CachedSender(object):
    def __init__(self, client):
        self.client = client
        self.lastMessage = None
    
    #convert message to jsonstr and then send if its new.
    def sendResult(self, message):
        message = json.dumps(message,indent=2)
        if (message == self.lastMessage):
            return
        else:
            self.lastMessage = message
            #print(message);
            self.client.sendMessage(message)
            
def sendResult(client, message):
    #print(message)
    jsonStr = json.dumps(message, indent=2)
    client.sendMessage(jsonStr)
        
if __name__ == '__main__':
    client = TCPClient.CreateClient('127.0.0.1',3338)
    cachedSender = CachedSender(client)
    main(cachedSender.sendResult)
    

        