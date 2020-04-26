import time
from PIL import Image

from nestris_ocr.capturing.base import AbstractCapture
from nestris_ocr.capturing.win32 import Win32UICapture
from nestris_ocr.capturing.win32_mgr import WindowMgr


class Win32Capture(AbstractCapture):
    def __init__(self, source_id):
        super().__init__(source_id)
        self.window_manager = WindowMgr()
        self.cap = Win32UICapture()

    def get_image(self) -> (int, Image):
        hwnd = self.get_window()

        image = self.cap.ImageCapture(
            None, hwnd
        )  # TODO @XaeL right now Win32UICapture requires the rectangle value, so this would not work
        return time.time(), image  # TODO @XaeL clean this timestamp up

    def get_window(self):
        for window in self.window_manager.getWindows():
            if window[1].startswith(self.source_id):
                return window[0]
        return None
