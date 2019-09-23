import time
import json
from config import config
import platform

if platform.system() == 'Darwin':
    import QuartzCapture as WindowCapture
    from QuartzWindowMgr import WindowMgr

else:
    import Win32UICapture as WindowCapture
    from Win32WindowMgr import WindowMgr
    
def checkWindow(hwnd):
    wm = WindowMgr()
    #check for hwnd passed in as none too.
    return wm.checkWindow(hwnd) if hwnd else None
    
def getWindow():
    wm = WindowMgr()

    windows = wm.getWindows()
    for window in windows:
        if window[1].startswith(config.WINDOW_NAME):
            return window[0]
    return None
    
def lerp(start, end, perc):
    return perc * (end-start) + start
    
def mult_rect(rect, mult):
    return (round(rect[2]*mult[0]+rect[0]),
            round(rect[3]*mult[1]+rect[1]),
            round(rect[2]*mult[2]),
            round(rect[3]*mult[3]))

def screenPercToPixels(w,h,rect_xywh):
    left = rect_xywh[0] * w
    top = rect_xywh[1] * h
    right = left + rect_xywh[2]*w
    bot = top+ rect_xywh[3]*h
    return (left,top,right,bot)

def runFunc(func, args):
    return func(*args)
    
#runs a bunch of tasks given a pool. Supports singleThread.
def runTasks(pool, rawTasks):
    result = {}
    if pool: #multithread
        tasks = []
        for task in rawTasks:
            tasks.append(pool.apply_async(task[0],task[1]))                
        taskResults = [res.get(timeout=1) for res in tasks]
        for key, number in taskResults:
            result[key] = number
        
    else: #single thread                   
        for task in rawTasks:
            key, number = runFunc(task[0],task[1])
            result[key] = number
            
    return result

#todo move this copy to Util.
def tryGetInt(x):
    try:
        return (True, round(float(x)))
    except:
        return (False, 0)

def tryGetFloat(x):
    try:
        return (True, float(x))
    except:
        return (False, 0)
        
