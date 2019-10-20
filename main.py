from functools import partial
from PIL import Image, ImageDraw
from OCRAlgo.DigitOCR import scoreImage
from OCRAlgo.ScoreFixer import ScoreFixer
from OCRAlgo.PieceStatsTextOCR import generate_stats
import OCRAlgo.PieceStatsBoardOCR as PieceStatsBoardOCR
import OCRAlgo.BoardOCR as BoardOCR
import OCRAlgo.PreviewOCR2 as PreviewOCR
from OCRAlgo.NewGameDetector import NewGameDetector

from calibrate import mainLoop as calibrateLoop
from config import config
from lib import * #bad!
from CachedSender import CachedSender
from multiprocessing import Pool
import multiprocessing
import threading
from Networking.NetworkClient import NetClient
from tkinter import messagebox, Tk
import time


#patterns for digits. 
#A = 0->9 + A->F, 
#D = 0->9
PATTERNS = {
    'score': 'ADDDDD' if config.hexSupport else 'DDDDDD',
    'lines': 'DDD',
    'level': 'AA',
    'stats': 'DDD'
}

STATS_METHOD  = config.stats_method #can be TEXT or FIELD.
CAPTURE_FIELD = config.capture_field
CAPTURE_PREVIEW = config.capture_preview
STATS_ENABLE  = config.capture_stats
USE_STATS_FIELD = (STATS_ENABLE and STATS_METHOD == 'FIELD')

# coords is supplied in XYWH format
def XYWHOffsetAndConvertToLTBR(offset, coords):
    return (
        coords[0] - offset[0],
        coords[1] - offset[1],
        coords[0] - offset[0] + coords[2],
        coords[1] - offset[1] + coords[3]
    )

# The list of tasks to execute can be computed at bootstrap time
# to remove all conditional processing from the main running loop
def getWindowAreaAndPartialTasks():
    # gather list of all areas that need capturing
    # that will be used to determine the minimum window area to capture
    areas = {
        'score': mult_rect(config.CAPTURE_COORDS,config.scorePerc),
        'lines': mult_rect(config.CAPTURE_COORDS,config.linesPerc),
        'level': mult_rect(config.CAPTURE_COORDS,config.levelPerc)
    }

    if CAPTURE_FIELD:
        areas['field'] = mult_rect(config.CAPTURE_COORDS, config.fieldPerc)
        areas['color1'] = mult_rect(config.CAPTURE_COORDS, config.color1Perc)
        areas['color2'] = mult_rect(config.CAPTURE_COORDS, config.color2Perc)

    if USE_STATS_FIELD:
        areas['stats2'] = mult_rect(config.CAPTURE_COORDS, config.stats2Perc)
    elif STATS_ENABLE:
        areas['stats'] = mult_rect(config.CAPTURE_COORDS, config.statsPerc)

    if CAPTURE_PREVIEW:
        areas['preview'] = mult_rect(config.CAPTURE_COORDS, config.previewPerc)

    coords_list = areas.values()

    # compute the minimum window area to capture to cover all fields
    minWindowAreaTLRB = (
        min((coords[0] for coords in coords_list)),
        min((coords[1] for coords in coords_list)),
        max((coords[0] + coords[2] for coords in coords_list)),
        max((coords[1] + coords[3] for coords in coords_list)),
    )

    # convert minimum window coordinates to XYWH (needed by capture API)
    minWindowAreaXYWH = (
        minWindowAreaTLRB[0],
        minWindowAreaTLRB[1],
        minWindowAreaTLRB[2] - minWindowAreaTLRB[0],
        minWindowAreaTLRB[3] - minWindowAreaTLRB[1]
    )

    # Extract offset from minimal capture area
    offset = minWindowAreaXYWH[:2]

    partials = []

    # prepare list of tasks to run at each loop
    for key, coords in areas.items():
        if key in ['score', 'lines', 'level']:
            partials.append(partial(
                extractAndOCR,
                XYWHOffsetAndConvertToLTBR(offset, coords),
                PATTERNS[key],
                key,
                False
            ))

        elif key == 'preview':
            partials.append(partial(
                extractAndOCRPreview,
                XYWHOffsetAndConvertToLTBR(offset, coords)
            ))

        elif key == 'stats':
            stats_coords = generate_stats(config.CAPTURE_COORDS, config.statsPerc ,config.scorePerc[3])

            for pieceKey, pieceCoords in stats_coords.items():
                partials.append(partial(
                    extractAndOCR,
                    XYWHOffsetAndConvertToLTBR(offset, pieceCoords),
                    PATTERNS[key],
                    pieceKey,
                    True
                ))

        elif key == 'stats2':
            # stats2 will only be read as a task in the main loop IF multithreading is disabled
            if MULTI_THREAD == 1:
                partials.append(partial(
                    extractAndOCRBoardPiece,
                    XYWHOffsetAndConvertToLTBR(offset, coords)
                ))

        elif key == 'field':
            partials.append(partial(
                extractAndOCRBoard,
                XYWHOffsetAndConvertToLTBR(offset, coords),
                XYWHOffsetAndConvertToLTBR(offset, areas['color1']),
                XYWHOffsetAndConvertToLTBR(offset, areas['color2'])
            ))

    return (minWindowAreaXYWH, partials)

#piece stats and method. Recommend using FIELD
STATS2_COORDS = mult_rect(config.CAPTURE_COORDS, config.stats2Perc)

MULTI_THREAD = config.threads #shouldn't need more than four if using FieldStats + score/lines/level

#limit how fast we scan.
RATE_FIELDSTATS = 0.004
RATE_TEXTONLY = 0.064
RATE_FIELD = 1.0 / clamp(15,60,config.scanRate)

if USE_STATS_FIELD and MULTI_THREAD == 1:    
    RATE = RATE_FIELDSTATS
elif CAPTURE_FIELD:
    RATE = RATE_FIELD
else:
    RATE = RATE_TEXTONLY

#how are we calculating timestamp? Time.time, or from the file?
firstTime = time.time()
def getRealTimeStamp():
    return time.time() - firstTime
    
getTimeStamp = getRealTimeStamp
if config.captureMethod == 'FILE':
    MULTI_THREAD = 1
    if config.netProtocol == 'FILE':
        RATE = 0.000        
        getTimeStamp = WindowCapture.TimeStamp

SLEEP_TIME = 0.001
def extractAndOCR(fieldCoords, digitPattern, taskName, red, img):
    return (taskName, scoreImage(img.crop(fieldCoords), digitPattern, False, red))

def extractAndOCRBoardPiece(boardPieceCoords, img):
    rgbo = PieceStatsBoardOCR.parseImage(img.crop(boardPieceCoords))
    return ('piece_stats_board', rgbo)

def extractAndOCRBoard(boardCoords, color1Coords, color2Coords, img):
    field = BoardOCR.parseImage(
        img.crop(boardCoords),
        img.crop(color1Coords),
        img.crop(color2Coords)
    )
    return ('field', field)

def extractAndOCRPreview(previewCoords, img):
    result = PreviewOCR.parseImage(img.crop(previewCoords))
    return ('preview', result)
    
def captureAndOCRBoardPiece(coords, hwnd):
    img = WindowCapture.ImageCapture(coords, hwnd)
    rgbo = PieceStatsBoardOCR.parseImage(img)    
    return ('piece_stats_board', rgbo)

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


def main(onCap, checkNetworkClose):    
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
    
    scoreFixer = ScoreFixer(PATTERNS['score'])
    
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

        windowMinCoords, partialTasks = getWindowAreaAndPartialTasks()
       
        while checkWindow(hwnd):
            # inner loop gets fresh data for just the desired window
            frame_start  = time.time()
            frame_end = frame_start + RATE

            img = WindowCapture.ImageCapture(windowMinCoords, hwnd)

            # inject captured image to complete partial tasks
            rawTasks = [(func, (img,)) for func in partialTasks]

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

            onCap(result, getTimeStamp())
            error = checkNetworkClose()   
            if error is not None:
                return error
            while time.time() < frame_end - SLEEP_TIME:
                time.sleep(SLEEP_TIME)
            
            if not WindowCapture.NextFrame(): #finished reading video
                break
    
if __name__ == '__main__':
    multiprocessing.freeze_support()
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == '--calibrate':
        calibrateLoop()
        sys.exit()


    print ("Creating net client...")
    client = NetClient.CreateClient(config.host,int(config.port))
    print ("Net client created.")
    cachedSender = CachedSender(client,config.printPacket,config.netProtocol)
    
    result = None
    try:
        print ("Starting main loop")
        result = main(cachedSender.sendResult, client.checkNetworkClose)
    except KeyboardInterrupt:
        pass
    print('main thread is here')
    print(result)
        
    if result is not None:
        #root = Tk()
        #root.withdraw()
        messagebox.showerror("NESTrisOCR", "You have been kicked. Reason: " + str(result)) 
        
    client.stop() 
    client.join()

