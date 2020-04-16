from FullStateOptimizer.FullStateOCR import FullStateOCR
from Networking.NetworkClient import NetClient
from calibrate import mainLoop as calibrateLoop
from CachedSender import CachedSender
from config import config
from lib import * #bad!


import multiprocessing
from tkinter import messagebox, Tk
import time
import sys


RATE = 1/60.0
print('ScanRate:' + str(RATE))
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



def main(onCap, checkNetworkClose):    
    BIG_BOI = 0.0
    finished = False
    while not finished:
        # outer loop waits for the window to exists
        frame_start = time.time()
        frame_end = frame_start + RATE
        hwnd = getWindow()

        if not hwnd:
            while time.time() < frame_end:
                time.sleep(SLEEP_TIME)
            continue

        
        fs_ocr = FullStateOCR(hwnd) 
        while checkWindow(hwnd):
            # inner loop gets fresh data for just the desired window
            frame_start  = time.time()
            frame_end = frame_start + RATE
            fs_ocr.update()
            result = fs_ocr.to_dict()
            processing_time = time.time() - frame_start
            #if processing_time > BIG_BOI:
            print(processing_time)
            #    BIG_BOI = processing_time
            print(result)
            #onCap(result, getTimeStamp())
            
            #error = checkNetworkClose()   
            #if error is not None:
            #    return error
            
            while time.time() < frame_end - SLEEP_TIME:
                time.sleep(SLEEP_TIME)
            
            #if not WindowCapture.NextFrame(): #finished reading video
            #    finished = True
            #    break

        print ('cleanexit')
    
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
    #try:
    print ("Starting main loop")
    result = main(cachedSender.sendResult, client.checkNetworkClose)
    #except KeyboardInterrupt:
    #    pass
    print('main thread is here')
    print(result)
        
    if result is not None:
        #root = Tk()
        #root.withdraw()
        messagebox.showerror("NESTrisOCR", "You have been kicked. Reason: " + str(result)) 
        
    client.stop() 
    client.join()

