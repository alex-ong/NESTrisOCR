from PIL import Image, ImageDraw
from OCRAlgo.DigitOCR import scoreImage
from OCRAlgo.ScoreFixer import ScoreFixer
from OCRAlgo.PieceStatsTextOCR import generate_stats
import OCRAlgo.PieceStatsBoardOCR as PieceStatsBoardOCR
import OCRAlgo.BoardOCR as BoardOCR
import OCRAlgo.PreviewOCR as PreviewOCR
from OCRAlgo.NewGameDetector import NewGameDetector

from calibrate import mainLoop as calibrateLoop
from config import config
from lib import * #bad!
from CachedSender import CachedSender
from multiprocessing import Pool
import multiprocessing
import threading
from Networking.NetworkClient import NetClient

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
FIELD_COORDS = mult_rect(config.CAPTURE_COORDS, config.fieldPerc)

STATS_METHOD  = config.stats_method #can be TEXT or FIELD. 

USE_STATS_FIELD = (STATS_ENABLE and STATS_METHOD == 'FIELD')

CAPTURE_FIELD = config.capture_field
COLOR1 = mult_rect(config.CAPTURE_COORDS, config.color1Perc)
COLOR2 = mult_rect(config.CAPTURE_COORDS, config.color2Perc)

CAPTURE_PREVIEW = config.capture_preview
PREVIEW_COORDS = mult_rect(config.CAPTURE_COORDS, config.previewPerc)

MULTI_THREAD = config.threads #shouldn't need more than four if using FieldStats + score/lines/level

#limit how fast we scan.
RATE_FIELDSTATS = 0.004
RATE_TEXTONLY = 0.064
RATE_FIELD = 1/60.0

if USE_STATS_FIELD and MULTI_THREAD == 1:    
    RATE = RATE_FIELDSTATS
elif CAPTURE_FIELD:
    RATE = RATE_FIELD
else:
    RATE = RATE_TEXTONLY

SLEEP_TIME = 0.001
def captureAndOCR(coords,hwnd,digitPattern,taskName,draw=False,red=False):    
    img = WindowCapture.ImageCapture(coords,hwnd)    
    return taskName, scoreImage(img,digitPattern,draw,red)
    
def captureAndOCRBoardPiece(coords, hwnd):
    img = WindowCapture.ImageCapture(coords, hwnd)
    rgbo = PieceStatsBoardOCR.parseImage(img)    
    return ('piece_stats_board', rgbo)

def captureAndOCRBoard(coords, hwnd):    
    img = WindowCapture.ImageCapture(coords, hwnd)
    col1 = WindowCapture.ImageCapture(COLOR1,hwnd)
    col2 = WindowCapture.ImageCapture(COLOR2,hwnd)    
    field = BoardOCR.parseImage(img,col1,col2)
    return ('field', field)

def captureAndOCRPreview(hwnd):
    img = WindowCapture.ImageCapture(PREVIEW_COORDS,hwnd)
    result = PreviewOCR.parseImage(img)
    return ('preview', result)

#run this as fast as possible    
def statsFieldMulti(ocr_stats, pool):
    while True:
        t = time.time()
        hwnd = getWindow()
        _, pieceType = pool.apply(captureAndOCRBoardPiece, (STATS2_COORDS, hwnd))
        ocr_stats.update(pieceType,t)
        if (time.time() - t > 1/60.0):
            print ("Warning, not scanning field fast enough", str(time.time() - t))
        
        # only sleep once.
        if time.time() < t + RATE_FIELDSTATS:
            time.sleep(SLEEP_TIME)


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
    
    gameIDParser = NewGameDetector()
    
    while True:
        # outer loop waits for the window to exists
        frame_start = time.time()
        frame_end = frame_start + RATE
        hwnd = getWindow()

        if not hwnd:
            while time.time() < frame_end:
                time.sleep(SLEEP_TIME)
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
                    for key in STATS_COORDS.keys():
                        rawTasks.append((captureAndOCR,(STATS_COORDS[key],hwnd,STATS_PATTERN,key,False,True)))
                elif MULTI_THREAD == 1: #run FIELD_PIECE in main thread if necessary
                    rawTasks.append((captureAndOCRBoardPiece, (STATS2_COORDS, hwnd)))
            
            if CAPTURE_FIELD:  
                rawTasks.append((captureAndOCRBoard,(FIELD_COORDS,hwnd)))
            
            if CAPTURE_PREVIEW:
                rawTasks.append((captureAndOCRPreview, (hwnd,)))

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
                if MULTI_THREAD == 1 and time.time() > frame_start + RATE_FIELD:
                    print ("Warning, dropped frame scanning preview in field")
            
            if config.capture_field and time.time() > frame_start + RATE_FIELD:
                print("Warning, dropped frame when capturing field")
            
            
            result['playername'] = config.player_name
            result['gameid'] = gameIDParser.getGameID(result['score'],result['lines'],result['level'])
            
            onCap(result)
                    
            while time.time() < frame_end - SLEEP_TIME:
                time.sleep(SLEEP_TIME)                        
        
if __name__ == '__main__':
    multiprocessing.freeze_support()
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == '--calibrate':
        calibrateLoop()
        sys.exit()
        
    print ("Creating net client...")
    client = NetClient.CreateClient(config.host,int(config.port))
    print ("Net client created.")
    cachedSender = CachedSender(client,config.printPacket)
    try:
        print ("Starting main loop")
        main(cachedSender.sendResult)
    except KeyboardInterrupt:
        pass
    print('main thread is here')
        
    client.stop()
    client.join()

        