import Xlib
import Xlib.display
from Xlib import X


class WindowMgr:
    """Encapsulates some calls for window management"""

    def __init__(self, hwnd=None):
        self.handle = hwnd

    def checkWindow(self, hwnd):
        """checks if a window still exists"""
        return hwnd

    def getWindows(self):
        """
        Return a list of tuples (handler, window name) for each real window.
        """
        windows = []

        def getWindowHierarchy(window, windows):
            children = window.query_tree().children
            for w in children:
                try:
                    w.get_image(0, 0, 1, 1, X.ZPixmap, 0xFFFFFFFF)
                    windows.append(
                        (
                            w.id,
                            w.get_wm_class()[1] if w.get_wm_class() is not None else "",
                        )
                    )
                except Xlib.error.BadMatch:
                    pass
                finally:
                    windows = getWindowHierarchy(w, windows)
            return windows

        root = Xlib.display.Display().screen().root
        windows = getWindowHierarchy(root, windows)
        return windows
