from Quartz import CGWindowListCreateDescriptionFromArray, CGWindowListCopyWindowInfo, kCGWindowListExcludeDesktopElements, kCGWindowListOptionOnScreenOnly, kCGNullWindowID

class WindowMgr:
    """Encapsulates some calls to the quartz for window management"""
    def __init__ (self):
        pass
  
    def checkWindow(self, hwnd):
        '''
        Checks if a window still exists
        '''
        return len(CGWindowListCreateDescriptionFromArray([hwnd])) == 1

    def getWindows(self):
        '''
        Return a list of tuples (win_id, win_title) for each real window.
        '''
        window_list = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements | kCGWindowListOptionOnScreenOnly, kCGNullWindowID)

        return [
            (win.valueForKey_('kCGWindowNumber'), win.valueForKey_('kCGWindowName'))
            for win in window_list
            if win.valueForKey_('kCGWindowSharingState') and win.valueForKey_('kCGWindowName')
        ]
