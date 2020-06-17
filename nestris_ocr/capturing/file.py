import cv2
from PIL import Image
from typing import Tuple

from nestris_ocr.capturing.base import AbstractCapture
from nestris_ocr.utils import xywh_to_ltrb
from nestris_ocr.types import XYWHBox


class FileCapture(AbstractCapture):
    def __init__(self, source_id: str, xywh_box: XYWHBox, extra_data: str) -> None:
        super().__init__(source_id, xywh_box, extra_data)

        self.cap = cv2.VideoCapture(source_id)
        if not self.cap.isOpened():
            raise Exception(f"Wrong file: {source_id}")

        self.frame_duration = 1.0 / self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.cur_frame = 0

    def get_image(self, rgb: bool = False) -> Tuple[float, Image.Image]:
        self.cur_frame += 1
        cv2_retval, cv2_image = self.cap.read()

        if not cv2_retval:
            return None, None

        if rgb:
            cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(cv2_image).crop(xywh_to_ltrb(self.xywh_box))
        ts = self.cur_frame * self.frame_duration

        return ts, image

    def fast_restart(self) -> bool:
        return False
