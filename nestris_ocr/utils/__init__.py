from nestris_ocr.types import LTRBBox, XYWHBox


def xywh_to_ltrb(xywh_box: XYWHBox) -> LTRBBox:
    x, y, w, h = xywh_box
    return (x, y, x + w, y + h)
