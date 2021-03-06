from abc import ABC, abstractmethod
from PIL import Image
from typing import Tuple

from nestris_ocr.types import XYWHBox
from nestris_ocr.capturing.deinterlacer import deinterlace, deinterlace_np


class AbstractCapture(ABC):
    def __init__(self, source_id: str, xywh_box: XYWHBox, extra_data: str) -> None:
        self.source_id = source_id
        self.xywh_box = xywh_box
        self.extra_data = extra_data

    @abstractmethod
    def get_image(self, rgb: bool = False) -> Tuple[float, Image.Image]:
        pass

    def stop(self) -> bool:
        pass

    # Deinterlaces a PIL.Image
    def deinterlace(self, image):
        return deinterlace(image)

    # Deinterlaces an opencv formatted image (w, h, bgr)
    def deinterlace_np(self, image):
        return deinterlace_np(image)

    @abstractmethod
    def fast_restart(self):
        pass

    def fast_reinit(self, source_id, xywh_box, extra_data):
        self.source_id = source_id
        self.xywh_box = xywh_box
        self.extra_data = extra_data
