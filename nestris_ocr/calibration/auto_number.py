import sys

from nestris_ocr.utils.lib import mult_rect
from nestris_ocr.calibration.draw_calibration import captureArea
from nestris_ocr.ocr_algo.digit import scoreImage0


def track_best_result(lowestScore, bestRect, result):
    newScore, newRect = result
    if lowestScore is None or (newScore is not None and newScore < lowestScore):
        return newScore, newRect
    return lowestScore, bestRect


def auto_adjust_numrect(capture_coords, rect, numDigits, updateUI):

    pattern = "D" * numDigits

    i = 0

    NES_WIDTH = 256.0
    NES_HEIGHT = 224.0
    NES_SUB_PIXELS = 4  # how accurate are we?
    SUB_PIXEL_PERC = 1.0 / NES_SUB_PIXELS
    left = (-1 // NES_SUB_PIXELS) * 2
    right = -left + 1
    total = (right - left) ** 4

    stock_img = captureArea(None, None)
    lowestScore = None
    bestRect = None
    # adjust width by up to 1px in any direction.
    for x in range(left, right):
        for y in range(left, right):
            for w in range(left, right):
                for h in range(left, right):
                    newRect = (
                        rect[0] + x * SUB_PIXEL_PERC / NES_WIDTH,
                        rect[1] + y * SUB_PIXEL_PERC / NES_HEIGHT,
                        rect[2] + w * SUB_PIXEL_PERC / NES_WIDTH,
                        rect[3] + h * SUB_PIXEL_PERC / NES_HEIGHT,
                    )
                    pixRect = mult_rect(capture_coords, newRect)
                    result = adjust_task(pixRect, pattern, newRect, stock_img)
                    i += 1
                    print_progress(i, total)
                    updateUI(i / float(total))
                    lowestScore, bestRect = track_best_result(
                        lowestScore, bestRect, result
                    )

    return bestRect


def adjust_task(pixRect, pattern, newRect, cached_image):
    result = 0
    img = captureArea(pixRect, cached_image)
    result = scoreImage0(img, pattern)

    return result, newRect


def print_progress(value, endvalue, bar_length=20):
    percent = float(value) / endvalue
    arrow = "-" * int(round(percent * bar_length) - 1) + ">"
    spaces = " " * (bar_length - len(arrow))

    sys.stdout.write(
        "\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100)))
    )
    sys.stdout.flush()
