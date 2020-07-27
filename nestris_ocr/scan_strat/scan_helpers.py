from PIL import Image
from math import ceil, floor
from nestris_ocr.config import config
from nestris_ocr.ocr_algo.digit import scoreImage as processDigits
from nestris_ocr.ocr_algo.board import parseImage as processBoard
from nestris_ocr.ocr_algo.preview2 import parseImage as processPreview
from nestris_ocr.ocr_algo.dasTrainerCurPiece import parseImage as processCurrentPiece
from nestris_ocr.ocr_algo.piece_stats_spawn import parseImage as processSpawn
from nestris_ocr.ocr_algo.piece_stats_text import generate_stats
from nestris_ocr.utils import xywh_to_ltrb
from nestris_ocr.utils.lib import mult_rect

PATTERNS = {
    "score": "DDDDDD",
    "lines": "DDD",
    "level": "TD",
    "stats": "DDD",
    "das": "BD",
}

if config["performance.support_hex_score"]:
    PATTERNS["score"] = "ADDDDD"

if config["performance.support_hex_level"]:
    PATTERNS["level"] = "AA"

# A few notes
# We always support scores past maxout
# We always support levels past 29


def get_window_areas():
    mapping = {
        "score": config["calibration.pct.score"],
        "lines": config["calibration.pct.lines"],
        "level": config["calibration.pct.level"],
        "field": config["calibration.pct.field"],
        "black_n_white": config["calibration.pct.black_n_white"],
        "stats2": config.stats2_percentages,
        "preview": config["calibration.pct.preview"],
        "flash": config["calibration.pct.flash"],
        # das trainer
        "current_piece": config["calibration.pct.das.current_piece"],
        "current_piece_das": config["calibration.pct.das.current_piece_das"],
        "instant_das": config["calibration.pct.das.instant_das"],
    }

    base_map = {
        key: xywh_to_ltrb(mult_rect(config["calibration.game_coords"], value))
        for key, value in mapping.items()
    }

    # stats are handled in a special manner
    base_map["stats"] = {
        piece: xywh_to_ltrb(coords)
        for (piece, coords) in generate_stats(
            config["calibration.game_coords"],
            config["calibration.pct.stats"],
            config["calibration.pct.score"][3],
        ).items()
    }

    # calibration of the color blocks include the edges (black),
    # and some of the "shine" white pixels
    # For the stats pieces, the color is in the lower-right quadrant of the piece block
    for color in ("color1", "color2"):
        x, y, w, h = mult_rect(
            config["calibration.game_coords"], config["calibration.pct." + color]
        )

        xywh = (
            x + floor(w * 0.5),
            y + floor(h * 0.5),
            ceil(w * 0.4),
            ceil(h * 0.4),
        )

        base_map[color] = xywh_to_ltrb(xywh)

    return base_map


WINDOW_AREAS = get_window_areas()


def refresh_window_areas():
    global WINDOW_AREAS
    WINDOW_AREAS = get_window_areas()


def mask_pattern(source, mask):
    result = ""
    for i, item in enumerate(source):
        if mask[i] == "X":
            result += "X"
        else:
            result += item
    return result


def get_sub_image(full_image, area):
    return full_image.crop(area)


def scan_text(full_image, pattern, digit_mask, window_area):
    mask = mask_pattern(pattern, digit_mask)
    sub_image = get_sub_image(full_image, window_area)
    return processDigits(sub_image, mask)


# scans the level image and returns a string
def scan_level(full_image):
    return scan_text(
        full_image, PATTERNS["level"], PATTERNS["level"], WINDOW_AREAS["level"]
    )


# scans the level image and returns a string. You can skip digits by inputting 'X' in the mask.
# "OOOXXX" means read first 3 digits
def scan_score(full_image, digit_mask="OOOOOO"):
    return scan_text(full_image, PATTERNS["score"], digit_mask, WINDOW_AREAS["score"])


def scan_lines(full_image, digit_mask="OOO"):
    return scan_text(full_image, PATTERNS["lines"], digit_mask, WINDOW_AREAS["lines"])


def scan_colors(full_image):
    color1 = get_sub_image(full_image, WINDOW_AREAS["color1"])
    color1 = color1.resize((1, 1), Image.BOX)
    color1 = color1.getpixel((0, 0))

    color2 = get_sub_image(full_image, WINDOW_AREAS["color2"])
    color2 = color2.resize((1, 1), Image.BOX)
    color2 = color2.getpixel((0, 0))

    return color1, color2


def scan_black_n_white(full_image):
    img_bnw = get_sub_image(full_image, WINDOW_AREAS["black_n_white"])
    img_bnw_mono = img_bnw.convert("L")

    whitest = 0x00 - 1
    whitest_coords = None

    blackest = 0xFF + 1
    blackest_coords = None

    for x in range(img_bnw_mono.width):
        for y in range(img_bnw_mono.height):

            value = img_bnw_mono.getpixel((x, y))

            if value > whitest:
                whitest = value
                whitest_coords = (x, y)

            if value < blackest:
                blackest = value
                blackest_coords = (x, y)

    black = img_bnw.getpixel(blackest_coords)
    white = img_bnw.getpixel(whitest_coords)

    return black, white


def scan_field(full_image, colors):
    sub_image = get_sub_image(full_image, WINDOW_AREAS["field"])
    return processBoard(sub_image, colors)


def scan_spawn(full_image, colors):
    sub_image = get_sub_image(full_image, WINDOW_AREAS["stats2"])
    return processSpawn(sub_image, colors)


def scan_stats_text(full_image, digit_mask="OOO"):
    pattern = mask_pattern(PATTERNS["stats"], digit_mask)
    res = {}

    for [piece, area] in WINDOW_AREAS["stats"].items():
        sub_image = get_sub_image(full_image, area)
        res[piece] = processDigits(sub_image, pattern, red=True)

    return res


def scan_preview(full_image, colors):
    sub_image = get_sub_image(full_image, WINDOW_AREAS["preview"])
    return processPreview(sub_image, colors)


def scan_das_current_piece(full_image, colors):
    sub_image = get_sub_image(full_image, WINDOW_AREAS["current_piece"])
    return processCurrentPiece(sub_image, colors)


def scan_das_current_piece_das(full_image, digit_mask="OO"):
    return scan_text(
        full_image, PATTERNS["das"], digit_mask, WINDOW_AREAS["current_piece_das"]
    )


def scan_das_instant_das(full_image, digit_mask="OO"):
    return scan_text(
        full_image, PATTERNS["das"], digit_mask, WINDOW_AREAS["instant_das"]
    )
