from config import config
from lib import WindowCapture
from OCRAlgo.DigitOCR import scoreImage as processDigits
from OCRAlgo.BoardOCR import parseImageSmart as processBoard
from OCRAlgo.PreviewOCR2 import parseImage as processPreview
from OCRAlgo.PieceStatsBoardOCR import parseImage as processSpawn
from FullStateOptimizer.WindowAreas import getWindowAreas

PATTERNS = {
    'score': 'ADDDDD',
    'lines': 'DDD',
    'level': 'AA',
    'stats': 'DDD',
    'das':   'BD'
}


# A few notes
# We always support scores past maxout
# We always support levels past 29

WINDOW_AREAS, FULL_RECT = getWindowAreas()
    

def mask_pattern(source, mask):
    result = ""
    for i, item in enumerate(source):
        if mask[i] == 'X':
            result += 'X'
        else:
            result += item
    return result

def scan_full(hwnd):
    return WindowCapture.ImageCapture(FULL_RECT, hwnd)

def scan_text(full_image, digit_mask, pattern, window_area):
    mask = mask_pattern(pattern, digit_mask)
    sub_image = full_image.crop(window_area)
    return processDigits(sub_image, mask)

# scans the level image and returns a string
def scan_level(full_image):
    return scan_text(full_image, PATTERNS['level'], PATTERNS[lines], WINDOW_AREAS['level'])

# scans the level image and returns a string. You can skip digits by inputting 'X' in the mask.
# "OOOXXX" means read first 3 digits
def scan_score(full_image, digit_mask):
    return scan_text(full_image, PATTERNS['score'], digit_mask, WINDOW_AREAS['score'])

def scan_lines(full_image, digit_mask):
    return scan_text(full_image, PATTERNS['lines'], digit_mask, WINDOW_AREAS['lines'])

def scan_field(full_image, color1=None, color2=None):
    sub_image = full_image.crop(WINDOW_AREAS['field'])

    cached = True
    if color1 is None and color2 is None:
        color1 = full_image.crop(WINDOW_AREAS['color1'])
        color2 = full_image.crop(WINDOW_AREAS['color2'])
        cached = False
    return processBoard(sub_image, color1, color2, cached)

def scan_spawn(full_image):
    sub_image = full_image.crop(WINDOW_AREAS['stats2'])
    return processSpawn(sub_image)

def scan_preview(full_image):
    sub_image = full_image.crop(WINDOW_AREAS['preview'])
    return processPreview(sub_image)

