import time
from PIL import Image
from typing import Tuple

from nestris_ocr.capturing.base import AbstractCapture
from nestris_ocr.capturing.quartz.quartz import QuartzCapture as Quartz
from nestris_ocr.capturing.quartz.quartz_mgr import WindowMgr
from nestris_ocr.types import XYWHBox


class QuartzCapture(AbstractCapture):
    def __init__(self, source_id: str, xywh_box: XYWHBox, extra_data: str) -> None:
        super().__init__(source_id, xywh_box, extra_data)
        self.window_manager = WindowMgr()
        self.cap = Quartz()

    def get_image(self, rgb: bool = False) -> Tuple[float, Image.Image]:
        hwnd = self.get_window()

        image = self.cap.ImageCapture(self.xywh_box, hwnd)
        # TODO add rgb support
        return time.time(), image  # use better timestamp

    def get_window(self):
        for window in self.window_manager.getWindows():
            if window[1].startswith(self.source_id):
                return window[0]
        return None

    def fast_restart(self) -> bool:
        return False
