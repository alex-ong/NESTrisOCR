'''
copied from http://nullege.com/codes/show/src@w@a@wallmanager-HEAD@mtmenu@window_manager.py/70/win32gui.EnumWindows
'''
import win32gui
import win32process
import win32con
import re
  
  
class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""
    def __init__ (self, hwnd = None):
        """Constructor"""
#        if not pid:
#            self.pid = win32process.GetCurrentProcessId ()
#        else:
#            self.pid = pid
        self._handle = hwnd
        #print "PID: %d -> %d" % (self.pid, win32process.GetCurrentProcessId())
  
    def find_window(self, class_name, window_name = None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)
  
    def _window_enum_callback(self, hwnd, list_apps):
        '''Pass to win32gui.EnumWindows() to check all the opened windows'''
  
        #print "CALBACK!"
        t, pid = win32process.GetWindowThreadProcessId(hwnd)
  
        list_apps.append((t, pid, win32gui.GetWindowText(hwnd)))
  
        if pid == self.pid and win32gui.GetWindowText(hwnd) == 'pymt':
            self._handle = hwnd
  
  
    def isRealWindow(self, hWnd):
        '''Return True iff given handler corespond to a real visible window on the desktop.'''
        if not win32gui.IsWindowVisible(hWnd):
            return False
        if win32gui.GetParent(hWnd) != 0:
            return False
        hasNoOwner = win32gui.GetWindow(hWnd, win32con.GW_OWNER) == 0
        lExStyle = win32gui.GetWindowLong(hWnd, win32con.GWL_EXSTYLE)
        if (((lExStyle & win32con.WS_EX_TOOLWINDOW) == 0 and hasNoOwner)
          or ((lExStyle & win32con.WS_EX_APPWINDOW != 0) and not hasNoOwner)):
            if win32gui.GetWindowText(hWnd):
                return True
        return False
  
    def getWindow(self, hwnd):
        return hwnd if win32gui.IsWindow(hwnd) else None

    def getWindows(self):
        '''
        Return a list of tuples (handler, (width, height)) for each real window.
        '''
        def callback(hWnd, windows):
            if not self.isRealWindow(hWnd):
                return
            text = win32gui.GetWindowText(hWnd)
            windows.append((hWnd, text))
        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows
    
    