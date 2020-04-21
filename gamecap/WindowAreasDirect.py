from config import config
from lib import mult_rect


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
    areas["color1"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.color1")
    )
    areas["color2"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.color2")
    )
    areas["stats2"] = mult_rect(
        config.get("calibration.game_coords"), config.stats2_percentages
    )
    areas["stats"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.stats")
    )
    areas["preview"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.preview")
    )
    areas["flash"] = mult_rect(
        config.get("calibration.game_coords"), config.get("calibration.pct.flash")
    )

    return areas, None
