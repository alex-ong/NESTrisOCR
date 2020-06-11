import time
from PIL import Image
from typing import Tuple

from nestris_ocr.capturing.base import AbstractCapture
from nestris_ocr.capturing.linux.linux import LinuxUICapture
from nestris_ocr.capturing.linux.linux_mgr import WindowMgr
from nestris_ocr.types import XYWHBox


class LinuxCapture(AbstractCapture):
    def __init__(self, source_id: str, xywh_box: XYWHBox, extra_data: str) -> None:
        super().__init__(source_id, xywh_box, extra_data)
        self.window_manager = WindowMgr()
        self.cap = LinuxUICapture()

    def get_image(self, rgb: bool = False) -> Tuple[float, Image.Image]:
        hwnd = self.get_window()

        image = self.cap.ImageCapture(self.xywh_box, hwnd)
        # TODO @Xael rgb support
        return time.time(), image  # TODO @XaeL fix timestamp

    def get_window(self):
        for window in self.window_manager.getWindows():
            if window[1].startswith(self.source_id):
                return window[0]
        return None

    def fast_restart(self) -> bool:
        return False
