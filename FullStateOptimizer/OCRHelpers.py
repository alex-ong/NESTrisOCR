from config import config
from OCRAlgo.DigitOCR import scoreImage
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

def scan_text(full_image, digit_mask, pattern, window_area):
    mask = mask_pattern(pattern, digit_mask)
    sub_image = full_image.crop(window_area)
    return scoreIimage(sub_image, mask)

# scans full level code
def scan_level(full_image):
    return scan_text(full_image, PATTERNS['level'], PATTERNS[lines], WINDOW_AREAS['level'])
    
def scan_score(full_image, digit_mask):
    return scan_text(full_image, PATTERNS['score'], digit_mask, WINDOW_AREAS['score'])

def scan_lines(full_image, digit_mask):
    return scan_text(full_image, PATTERNS['lines'], digit_mask, WINDOW_AREAS['lines'])