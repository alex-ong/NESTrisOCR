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
from textstats import generate_stats
from lib import mult_rect, lerp, ScoreFixer
import boardocr
import json
import time




#patterns for digits. 
#A = 0->9 + A->F, 
#D = 0->9
SCORE_PATTERN = 'ADDDDD' #change to DDDDDD if you don't have A-F enabled.
LINES_PATTERN = 'DDD'
LEVEL_PATTERN = 'AA'
STATS_PATTERN = 'DDD'

SCORE_COORDS = mult_rect(CAPTURE_COORDS,scorePerc)
LINES_COORDS = mult_rect(CAPTURE_COORDS,linesPerc)
LEVEL_COORDS = mult_rect(CAPTURE_COORDS,levelPerc)

#piece stats and method. Recommend using FIELD
STATS_ENABLE  = False
STATS_COORDS  = generate_stats(CAPTURE_COORDS,statsPerc,scorePerc[3])
STATS2_COORDS = mult_rect(CAPTURE_COORDS, stats2Perc)
STATS_METHOD  = 'FIELD' #can be TEXT or FIELD. 

USE_STATS_FIELD = (STATS_ENABLE and STATS_METHOD == 'FIELD')

CALIBRATION = True
MULTI_THREAD = 1 #shouldn't need more than four if using FieldStats + score/lines/level

#limit how fast we scan.
RATE_FIELDSTATS = 0.008
RATE_TEXTONLY = 0.064

if USE_STATS_FIELD:    
    RATE = RATE_FIELDSTATS
else:
    RATE = RATE_TEXTONLY

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
        for x in range (4):
            for y in range(2):                
                blockPercX = lerp(stats2Perc[0], stats2Perc[0]+stats2Perc[2], x/4.0 + 1/8.0)
                blockPercY = lerp(stats2Perc[1], stats2Perc[1]+stats2Perc[3], y/2.0 + 1/4.0)
                rect = (blockPercX-0.01, blockPercY-0.01, 0.02, 0.02)
                draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=red)
        
    img.paste(poly,mask=poly)    
    del draw
    
def calibrate():
    hwnd = getWindow()
    if hwnd is None:
        print ("Unable to find OBS window with title:",  WINDOW_NAME)
        return
    
    img = WindowCapture.ImageCapture(CAPTURE_COORDS,hwnd)
    highlight_calibration(img)
    img.show()

    return

def captureAndOCR(coords,hwnd,digitPattern,taskName,draw=False,red=False):
    t = time.time()
    img = WindowCapture.ImageCapture(coords,hwnd)    
    return taskName, scoreImage(img,digitPattern,draw,red)

#this is a stub. Don't use it!
def captureAndOCRBoard(coords, hwnd):
    img = WindowCapture.ImageCapture(coords, hwnd)
    rgbo = boardocr.parseImage(img)    
    return ('board_ocr', rgbo)

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
    
    if USE_STATS_FIELD:
        accum = boardocr.OCRStatus()
        lastLines = None
    
    scoreFixer = ScoreFixer(SCORE_PATTERN)
    
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
            
            # update our accumulator
            if USE_STATS_FIELD:            
                if lastLines is None and result['lines'] == '000':
                    accum.reset()
                accum.update(result['board_ocr'], t)
                del result['board_ocr']
                result.update(accum.toDict())
                lastLines = result['lines']
            
            #fix score's first digit. 8 to B and B to 8 depending on last state.
            result['score'] = scoreFixer.fix(result['score'])
            
            onCap(result) 
            
        if (time.time() - t > 0.016 and
            STATS_ENABLE and STATS_METHOD == 'FIELD'):
            print("Warning, not meeting rate")
        
        while time.time() < t + RATE:
            time.sleep(0.001)
        
class CachedSender(object):
    def __init__(self, client):
        self.client = client
        self.lastMessage = None
        self.lastSend = time.time()
        
    #convert message to jsonstr and then send if its new.
    def sendResult(self, message):     
        jsonMessage = json.dumps(message,indent=2)        
        t = time.time()
        if t - self.lastSend > 0.064 or (self.lastMessage != jsonMessage):            
            print(message)
            self.client.sendMessage(jsonMessage)
            self.lastMessage = jsonMessage
            self.lastSend = time.time()

    
def sendResult(client, message):    
    jsonStr = json.dumps(message, indent=2)
    client.sendMessage(jsonStr)
        
if __name__ == '__main__':
    client = TCPClient.CreateClient('127.0.0.1',3338)
    cachedSender = CachedSender(client)
    main(cachedSender.sendResult)
    

        