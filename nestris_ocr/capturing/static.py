from PIL import Image

from typing import Tuple

from nestris_ocr.capturing.base import AbstractCapture
from nestris_ocr.utils import xywh_to_ltrb
from nestris_ocr.types import XYWHBox
import nestris_ocr.utils.time as time


class StaticCapture(AbstractCapture):
    def __init__(self, source_id: str, xywh_box: XYWHBox) -> None:
        super().__init__(source_id, xywh_box)
        self.set_source_id(source_id)

    def set_source_id(self, source_id: str):
        self.source_img = Image.open(source_id)

    def get_image(self, rgb: bool = False) -> Tuple[float, Image.Image]:
        return time.time(), self.source_img.crop(xywh_to_ltrb(self.xywh_box))

    def fast_restart(self) -> bool:
        return False
