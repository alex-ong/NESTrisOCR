from nestris_ocr.capturing.base import AbstractCapture
from nestris_ocr.types import XYWHBox
from typing import Tuple
from PIL import Image
import time


# Null capture class; always returns black frames.
class NullCapture(AbstractCapture):
    def __init__(self, source_id: str, xywh_box: XYWHBox, extra_data: str) -> None:
        super().__init__(source_id, xywh_box, extra_data)

    def get_image(self, rgb: bool = False) -> Tuple[float, Image.Image]:
        w, h = self.xywh_box[2], self.xywh_box[3]
        im = Image.new("RGB", (w, h))
        return (time.time(), im)
