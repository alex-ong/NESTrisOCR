from PIL import Image, ImageDraw
from OCRAlgo.DigitOCR import scoreImage
from OCRAlgo.ScoreFixer import ScoreFixer
from OCRAlgo.PieceStatsTextOCR import generate_stats
import OCRAlgo.PieceStatsBoardOCR as PieceStatsBoardOCR

from config import config
from lib import * #bad!
from CachedSender import CachedSender
from multiprocessing import Pool
import threading
from Networking import TCPClient


import time


#patterns for digits. 
#A = 0->9 + A->F, 
#D = 0->9
SCORE_PATTERN = 'ADDDDD' if config.hexSupport else 'DDDDDD'
LINES_PATTERN = 'DDD'
LEVEL_PATTERN = 'AA'
STATS_PATTERN = 'DDD'

SCORE_COORDS = mult_rect(config.CAPTURE_COORDS,config.scorePerc)
LINES_COORDS = mult_rect(config.CAPTURE_COORDS,config.linesPerc)
LEVEL_COORDS = mult_rect(config.CAPTURE_COORDS,config.levelPerc)

#piece stats and method. Recommend using FIELD
STATS_ENABLE  = config.capture_stats
STATS_COORDS  = generate_stats(config.CAPTURE_COORDS,config.statsPerc,config.scorePerc[3])
STATS2_COORDS = mult_rect(config.CAPTURE_COORDS, config.stats2Perc)
STATS_METHOD  = config.stats_method #can be TEXT or FIELD. 

USE_STATS_FIELD = (STATS_ENABLE and STATS_METHOD == 'FIELD')

MULTI_THREAD = config.threads #shouldn't need more than four if using FieldStats + score/lines/level

#limit how fast we scan.
RATE_FIELDSTATS = 0.004
RATE_TEXTONLY = 0.064

if USE_STATS_FIELD and MULTI_THREAD == 1:    
    RATE = RATE_FIELDSTATS
else:
    RATE = RATE_TEXTONLY

def captureAndOCR(coords,hwnd,digitPattern,taskName,draw=False,red=False):
    t = time.time()
    img = WindowCapture.ImageCapture(coords,hwnd)    
    return taskName, scoreImage(img,digitPattern,draw,red)

def captureAndOCRBoard(coords, hwnd):
    img = WindowCapture.ImageCapture(coords, hwnd)
    rgbo = PieceStatsBoardOCR.parseImage(img)    
    return ('piece_stats_board', rgbo)

#run this as fast as possible    
def statsFieldMulti(ocr_stats, pool):
    while True:
        t = time.time()
        hwnd = getWindow()
        _, pieceType = pool.apply(captureAndOCRBoard, (STATS2_COORDS, hwnd))
        ocr_stats.update(pieceType,t)
        if (time.time() - t > 1/60.0):
            print ("Warning, not scanning field fast enough", str(time.time() - t))
        
        # only sleep once.
        if time.time() < t + RATE_FIELDSTATS:
            time.sleep(0.001)


def main(onCap):    
    if MULTI_THREAD >= 2:
        p = Pool(MULTI_THREAD)    
    else:
        p = None

    if USE_STATS_FIELD:
        accum = PieceStatsBoardOCR.OCRStatus()
        lastLines = None #use to reset accumulator
        if MULTI_THREAD >= 2: #run Field_OCR as fast as possible; unlock from mainthread.
            thread = threading.Thread(target=statsFieldMulti, args=(accum,p))
            thread.daemon = True
            thread.start()        
    
    scoreFixer = ScoreFixer(SCORE_PATTERN)
    
    
    while True:
        # outer loop waits for the window to exists
        frame_start = time.time()
        frame_end = frame_start + RATE
        hwnd = getWindow()

        if not hwnd:
            while time.time() < frame_end:
                time.sleep(0.001)
            continue

        while checkWindow(hwnd):
            # inner loop gets fresh data for just the desired window
            frame_start  = time.time()
            frame_end = frame_start + RATE

            result = {}
            rawTasks = []
            rawTasks.append((captureAndOCR,(SCORE_COORDS,hwnd,SCORE_PATTERN,"score")))
            rawTasks.append((captureAndOCR,(LINES_COORDS,hwnd,LINES_PATTERN,"lines")))
            rawTasks.append((captureAndOCR,(LEVEL_COORDS,hwnd,LEVEL_PATTERN,"level")))
            
            if STATS_ENABLE:
                if STATS_METHOD == 'TEXT':                
                    rawTasks.append((captureAndOCR,(STATS_COORDS[key],hwnd,STATS_PATTERN,key,False,True)))
                elif MULTI_THREAD == 1: #run FIELD_PIECE in main thread if necessary
                    rawTasks.append((captureAndOCRBoard, (STATS2_COORDS, hwnd)))
                    
            # run all tasks (in separate threads if MULTI_THREAD is enabled)
            result = runTasks(p, rawTasks)

            #fix score's first digit. 8 to B and B to 8 depending on last state.
            result['score'] = scoreFixer.fix(result['score'])
            
            # update our accumulator
            if USE_STATS_FIELD:
                if lastLines is None and result['lines'] == '000':
                    accum.reset()
                
                if MULTI_THREAD == 1:
                    accum.update(result['piece_stats_board'], frame_start)
                    del result['piece_stats_board']

                result.update(accum.toDict())
                lastLines = result['lines']
            
                # warning for USE_STATS_FIELD if necessary
                if MULTI_THREAD == 1 and time.time() > frame_start + 1/60.0:
                    print ("Warning, not scanning field fast enough")
                    
            onCap(result)
        
            while time.time() < frame_end:
                time.sleep(0.001)
        

        
if __name__ == '__main__':
    client = TCPClient.CreateClient('127.0.0.1',3338)
    cachedSender = CachedSender(client)
    try:
        main(cachedSender.sendResult)
    except KeyboardInterrupt:
        pass
    client.stop()
    client.join()

        