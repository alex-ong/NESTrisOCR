from nestris_ocr.config import config
from nestris_ocr.utils.lib import mult_rect


# coords is supplied in XYWH format
def XYWHOffsetAndConvertToLTBR(offset, coords):
    return (
        coords[0] - offset[0],
        coords[1] - offset[1],
        coords[0] - offset[0] + coords[2],
        coords[1] - offset[1] + coords[3],
    )


def getWindowAreas():
    # gather list of all areas that need capturing
    # that will be used to determine the minimum window area to capture
    areas = {}
    areas["score"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.score"]
    )
    areas["lines"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.lines"]
    )
    areas["level"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.level"]
    )
    areas["field"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.field"]
    )

    # Todo: config.color_method == DYNAMIC vs LOOKUP
    areas["color1"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.color1"]
    )
    areas["color2"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.color2"]
    )

    # Don't add all window_areas; only the ones we use.
    if config["calibration.capture_preview"]:
        areas["preview"] = mult_rect(
            config["calibration.game_coords"], config["calibration.pct.preview"]
        )
    if config["stats.enabled"]:
        if config["stats.capture_method"] == "FIELD":
            areas["stats2"] = mult_rect(
                config["calibration.game_coords"], config.stats2_percentages
            )
        if config["stats.capture_method"] == "TEXT":
            areas["stats"] = mult_rect(
                config["calibration.game_coords"], config["calibration.pct.stats"],
            )
    if config["calibration.flash_method"] == "BACKGROUND":
        areas["flash"] = mult_rect(
            config["calibration.game_coords"], config["calibration.pct.flash"]
        )

    coords_list = areas.values()

    # compute the minimum window area to capture to cover all fields
    minWindowAreaTLRB = (
        min((coords[0] for coords in coords_list)),
        min((coords[1] for coords in coords_list)),
        max((coords[0] + coords[2] for coords in coords_list)),
        max((coords[1] + coords[3] for coords in coords_list)),
    )

    # convert minimum window coordinates to XYWH (needed by capture API)
    minWindowAreaXYWH = (
        minWindowAreaTLRB[0],
        minWindowAreaTLRB[1],
        minWindowAreaTLRB[2] - minWindowAreaTLRB[0],
        minWindowAreaTLRB[3] - minWindowAreaTLRB[1],
    )

    # Extract offset from minimal capture area
    offset = minWindowAreaXYWH[:2]
    for key in areas:
        areas[key] = XYWHOffsetAndConvertToLTBR(offset, areas[key])

    return areas, minWindowAreaXYWH
