from typing import Tuple


def xywh_to_ltrb(xywh_box: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    x, y, w, h = xywh_box
    return (x, y, x + w, y + h)
