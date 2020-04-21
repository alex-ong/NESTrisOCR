from config import config
from lib import mult_rect, XYWHOffsetAndConvertToLTBR


def getWindowAreas():
    # gather list of all areas that need capturing
    # that will be used to determine the minimum window area to capture
    areas = {}
    areas["score"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.score")
    )
    areas["lines"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.lines")
    )
    areas["level"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.level")
    )
    areas["field"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.field")
    )

    # Todo: config.color_method == DYNAMIC vs LOOKUP
    areas["color1"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.color1")
    )
    areas["color2"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.color2")
    )

    # Don't add all window_areas; only the ones we use.
    if config.get("calibration.capture_preview"):
        areas["preview"] = mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.preview")
        )
    if config.get("stats.enabled"):
        if config.get("stats.capture_method") == "FIELD":
            areas["stats2"] = mult_rect(
                config.get("calibration.game_coords"), config.stats2_percentages
            )
        if config.get("stats.capture_method") == "TEXT":
            areas["stats"] = mult_rect(
                config.get("calibration.game_coords"),
                config.get("calibration.pct.stats"),
            )
    if config.get("calibration.flash_method") == "BACKGROUND":
        areas["flash"] = mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.flash")
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
