import Quartz
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListExcludeDesktopElements, kCGWindowListOptionOnScreenOnly, kCGNullWindowID, CGWindowListCreateImage,  CGRectNull, kCGWindowListOptionIncludingWindow

def getWindowInfo(win):
    coordinates = win.valueForKey_('kCGWindowBounds')

    return {
        'ID': win.valueForKey_('kCGWindowNumber'),
        'x':  coordinates.valueForKey_('X'),
        'y':  coordinates.valueForKey_('Y'),
        'w':  coordinates.valueForKey_('Width'),
        'h':  coordinates.valueForKey_('Height'),
    }

class WindowMgr:
    """Encapsulates some calls to the quartz for window management"""
    def __init__ (self):
        pass
  
    def checkWindow(self, win_info):
        '''
        Checks if a window still exists
        '''
        try:
            win = Quartz.CGWindowListCreateDescriptionFromArray([win_info['ID']])[0]
            return getWindowInfo(win)
        except:
            return None

    def getWindows(self):
        '''
        Return a list of tuples (win_info, win_title) for each real window.
        '''
        window_list = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements | kCGWindowListOptionOnScreenOnly, kCGNullWindowID)

        filtered_list = []

        for win in window_list:
            if (win.valueForKey_('kCGWindowIsOnscreen')
                and win.valueForKey_('kCGWindowSharingState')
                and win.valueForKey_('kCGWindowName')
            ):
                # weird format to match the win32 setup :/
                filtered_list.append((
                    getWindowInfo(win),
                    win.valueForKey_('kCGWindowName')
                ))

        return filtered_list
