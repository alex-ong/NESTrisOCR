try:
    import win32ui
    import win32gui
    import win32con
    import pywintypes        
except ImportError:
    print('Please run "pip install pypiwin32"')

try:
    from PIL import Image
except ImportError:
    print('Please run "pip install pillow"')


class Win32UICapture(object):
    def __init__(self):
        self.lastRectangle = None
        self.lasthwndTarget = None
        self.hDC = None
        self.myDC = None
        self.newDC = None
        self.myBitMap = None
    
    def InitAll(self):
        hwnd = self.lasthwndTarget
        x, y, w, h = self.lastRectangle
        self.hDC = win32gui.GetDC(hwnd)
        self.myDC = win32ui.CreateDCFromHandle(self.hDC)
        self.newDC = self.myDC.CreateCompatibleDC()
            
        self.myBitMap = win32ui.CreateBitmap()
        self.myBitMap.CreateCompatibleBitmap(self.myDC, w, h)
        
        self.newDC.SelectObject(self.myBitMap)
 
    def ReleaseAll(self):    
        hwnd = self.lasthwndTarget
        if self.myDC is not None:
            try:
                self.myDC.DeleteDC()                
            except win32ui.error:
                pass
            finally:
                self.myDC = None
                
        if self.newDC is not None:
            try:
                self.newDC.DeleteDC()
            except win32ui.error:
                pass
            finally:
                self.newDC = None
                
        if self.hDC is not None:            
            win32gui.ReleaseDC(hwnd, self.hDC)            
            self.hDC = None
                
        if self.myBitMap is not None:
            win32gui.DeleteObject(self.myBitMap.GetHandle())    
            self.myBitMap = None

    def ImageCapture(self, rectangle, hwndTarget):    
        x, y, w, h = rectangle
        hwnd = hwndTarget
        if w <= 0 or h <= 0 or hwnd == 0:
            return None        

        try:        
            if self.lastRectangle != rectangle or self.lasthwndTarget != hwndTarget:
                self.ReleaseAll()
                self.lastRectangle = rectangle
                self.lasthwndTarget = hwndTarget 
                self.InitAll()
            
            self.newDC.BitBlt((0, 0), (w, h) , self.myDC, (x, y), win32con.SRCCOPY)
            self.myBitMap.Paint(self.newDC)
            bmpinfo = self.myBitMap.GetInfo()
            bmpstr = self.myBitMap.GetBitmapBits(True)
            im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
            # im.save("C:/temp/temp.png")
            # Free Resources            
            return im
        except pywintypes.error:
            raise
        except win32ui.error:
            raise
        return None

imgCap = Win32UICapture()
def ImageCapture(rectangle, hwndTarget):
    global imgCap
    return imgCap.ImageCapture(rectangle,hwndTarget)

def NextFrame():
    return True