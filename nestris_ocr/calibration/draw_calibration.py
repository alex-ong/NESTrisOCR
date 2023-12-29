from PIL import Image, ImageDraw

from nestris_ocr.capturing import uncached_capture
from nestris_ocr.utils import xywh_to_ltrb
from nestris_ocr.utils.lib import (
    screenPercToPixels,
    lerp,
    mult_rect,
)
from nestris_ocr.ocr_algo.piece_stats_text import generate_stats
from nestris_ocr.ocr_algo.preview import calculateOffsets

red = (255, 0, 0, 128)
green = (0, 255, 0, 128)
blue = (0, 100, 255, 128)
orange = (255, 165, 0, 128)
yellow = (255, 255, 0, 128)


# splits rectangle by digits.
# assumes 7 pixels with 1 pixel gaps.
def splitRect(perc, count):
    totalPixels = count * 7 + count - 1
    width = perc[2]
    singlePixel = width / totalPixels

    result = []
    for i in range(count):
        result.append(
            [perc[0] + singlePixel * 8 * i, perc[1], 7 * singlePixel, perc[3]]
        )
    return result


def captureArea(coords=None, image=None):
    if image is None:
        _, image = uncached_capture().get_image(rgb=True)

    if not coords:
        return image

    return image.crop(xywh_to_ltrb(coords))


def capture_split_digits(c):
    scorePix = mult_rect(c["calibration.game_coords"], c["calibration.pct.score"])
    linesPix = mult_rect(c["calibration.game_coords"], c["calibration.pct.lines"])
    levelPix = mult_rect(c["calibration.game_coords"], c["calibration.pct.level"])

    scoreImg = captureArea(scorePix)
    linesImg = captureArea(linesPix)
    levelImg = captureArea(levelPix)

    return scoreImg, linesImg, levelImg


def capture_preview(c):
    previewPix = mult_rect(c["calibration.game_coords"], c["calibration.pct.preview"])
    previewImg = captureArea(previewPix)
    return previewImg


def capture_color1color2(c):
    color1Pix = mult_rect(c["calibration.game_coords"], c["calibration.pct.color1"])
    color1Img = captureArea(color1Pix)

    color2Pix = mult_rect(c["calibration.game_coords"], c["calibration.pct.color2"])
    color2Img = captureArea(color2Pix)

    return color1Img, color2Img


def capture_blackwhite(c):
    blackWhitePix = mult_rect(
        c["calibration.game_coords"], c["calibration.pct.black_n_white"]
    )
    blackWhiteImg = captureArea(blackWhitePix)

    return blackWhiteImg


def capture_das_trainer(c):
    currentPiecePix = mult_rect(
        c["calibration.game_coords"], c["calibration.pct.das.current_piece"]
    )
    currentPieceImg = captureArea(currentPiecePix)

    currentPieceDasPix = mult_rect(
        c["calibration.game_coords"], c["calibration.pct.das.current_piece_das"]
    )
    currentPieceDasImg = captureArea(currentPieceDasPix)

    instantDasPix = mult_rect(
        c["calibration.game_coords"], c["calibration.pct.das.instant_das"]
    )
    instantDasImg = captureArea(instantDasPix)

    return currentPieceImg, currentPieceDasImg, instantDasImg


def highlight_calibration(img, c):
    poly = Image.new("RGBA", (img.width, img.height))
    draw = ImageDraw.Draw(poly)

    scorePerc, linesPerc, levelPerc = (
        c["calibration.pct.score"],
        c["calibration.pct.lines"],
        c["calibration.pct.level"],
    )

    for rect in splitRect(linesPerc, 3):  # lines
        draw.rectangle(screenPercToPixels(img.width, img.height, rect), fill=red)

    for rect in splitRect(scorePerc, 6):  # score
        draw.rectangle(screenPercToPixels(img.width, img.height, rect), fill=green)

    for rect in splitRect(levelPerc, 2):
        draw.rectangle(
            screenPercToPixels(img.width, img.height, rect), fill=blue
        )  # level

    if c["calibration.dynamic_black_n_white"]:
        highlight_calibration_blackwhite(img, c, draw)

    if c["calibration.capture_field"]:
        highlight_calibration_field(img, c, draw)

        if c["calibration.dynamic_colors"]:
            highlight_calibration_color1color2(img, c, draw)

    if c["stats.enabled"]:
        if c["stats.capture_method"] == "TEXT":
            # pieces
            for value in generate_stats(
                c["calibration.game_coords"],
                c["calibration.pct.stats"],
                c["calibration.pct.score"][3],
                False,
            ).values():
                draw.rectangle(
                    screenPercToPixels(img.width, img.height, value), fill=orange
                )
        else:  # c["stats.capture_method"] == "FIELD":
            stats2_percentages = c.stats2_percentages
            for x in range(4):
                for y in range(2):
                    blockPercX = lerp(
                        stats2_percentages[0],
                        stats2_percentages[0] + stats2_percentages[2],
                        x / 4.0 + 1 / 8.0,
                    )
                    blockPercY = lerp(
                        stats2_percentages[1],
                        stats2_percentages[1] + stats2_percentages[3],
                        y / 2.0 + 1 / 4.0,
                    )
                    rect = (blockPercX - 0.01, blockPercY - 0.01, 0.02, 0.02)
                    draw.rectangle(
                        screenPercToPixels(img.width, img.height, rect), fill=blue
                    )

    if c["calibration.capture_preview"]:
        highlight_calibration_preview(img, c, draw)

    if c["calibration.flash_method"] == "BACKGROUND":
        draw.rectangle(
            screenPercToPixels(img.width, img.height, c["calibration.pct.flash"]),
            fill=yellow,
        )

    if c["calibration.capture_das"]:
        highlight_calibration_das(img, c, draw)

    img.paste(poly, mask=poly)
    del draw


def highlight_calibration_field(img, c, draw):
    fieldPerc = c["calibration.pct.field"]
    for x in range(10):
        for y in range(20):
            blockPercX = lerp(
                fieldPerc[0], fieldPerc[0] + fieldPerc[2], x / 10.0 + 1 / 20.0
            )
            blockPercY = lerp(
                fieldPerc[1], fieldPerc[1] + fieldPerc[3], y / 20.0 + 1 / 40.0
            )
            rect = (blockPercX - 0.01, blockPercY - 0.01, 0.02, 0.02)
            draw.rectangle(screenPercToPixels(img.width, img.height, rect), fill=red)


def highlight_calibration_color1color2(img, c, draw):
    draw.rectangle(
        screenPercToPixels(img.width, img.height, c["calibration.pct.color1"]),
        fill=orange,
    )
    draw.rectangle(
        screenPercToPixels(img.width, img.height, c["calibration.pct.color2"]),
        fill=orange,
    )


def highlight_calibration_blackwhite(img, c, draw):
    draw.rectangle(
        screenPercToPixels(img.width, img.height, c["calibration.pct.black_n_white"]),
        fill=orange,
    )


def highlight_calibration_preview(img, c, draw):
    draw.rectangle(
        screenPercToPixels(img.width, img.height, c["calibration.pct.preview"]),
        fill=blue,
    )

    pixelWidth = c["calibration.pct.preview"][2] / 31.0
    pixelHeight = c["calibration.pct.preview"][3] / 15.0

    blockWidth = pixelWidth * 7
    blockHeight = pixelHeight * 7

    t1 = (
        c["calibration.pct.preview"][0] + 4 * pixelWidth,
        c["calibration.pct.preview"][1],
        blockWidth,
        blockHeight,
    )
    t2 = (
        c["calibration.pct.preview"][0] + 12 * pixelWidth,
        c["calibration.pct.preview"][1],
        blockWidth,
        blockHeight,
    )
    t3 = (
        c["calibration.pct.preview"][0] + 20 * pixelWidth,
        c["calibration.pct.preview"][1],
        blockWidth,
        blockHeight,
    )
    t4 = (
        c["calibration.pct.preview"][0] + 12 * pixelWidth,
        c["calibration.pct.preview"][1] + pixelHeight * 8,
        blockWidth,
        blockHeight,
    )

    for rect in [t1, t2, t3, t4]:
        draw.rectangle(screenPercToPixels(img.width, img.height, rect), fill=orange)

    for o in calculateOffsets():
        rect = (o[0], o[1], pixelWidth, pixelHeight)
        draw.rectangle(screenPercToPixels(img.width, img.height, rect), fill="red")


def highlight_calibration_das(img, c, draw):
    for rect in splitRect(c["calibration.pct.das.current_piece_das"], 2):
        draw.rectangle(screenPercToPixels(img.width, img.height, rect), fill=green)

    for rect in splitRect(c["calibration.pct.das.instant_das"], 2):
        draw.rectangle(screenPercToPixels(img.width, img.height, rect), fill=red)

    draw.rectangle(
        screenPercToPixels(
            img.width, img.height, c["calibration.pct.das.current_piece"]
        ),
        fill=blue,
    )


# todo, return image or array of images with cropped out sections.
def draw_calibration(config):
    try:
        uncached_capture().set_source_id(config["capture.source_id"])
    except AttributeError:
        pass
    except FileNotFoundError:
        pass

    img = captureArea()
    if config["capture.method"] == "FILE":
        for i in range(10):
            uncached_capture().get_image(rgb=True)
    highlight_calibration(img, config)
    img = img.resize((512, 448), Image.LANCZOS)
    return img
