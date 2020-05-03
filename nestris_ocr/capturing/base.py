from abc import ABC, abstractmethod
from PIL import Image
from typing import Tuple

from nestris_ocr.types import XYWHBox


class AbstractCapture(ABC):
    def __init__(self, source_id: str, xywh_box: XYWHBox) -> None:
        self.source_id = source_id
        self.xywh_box = xywh_box

    @abstractmethod
    def get_image(self, rgb: bool = False) -> Tuple[float, Image.Image]:
        pass
