from nestris_ocr.config import config
from nestris_ocr.utils.lib import mult_rect


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
    areas["color1"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.color1"]
    )
    areas["color2"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.color2"]
    )
    areas["stats2"] = mult_rect(
        config["calibration.game_coords"], config.stats2_percentages
    )
    areas["stats"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.stats"]
    )
    areas["preview"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.preview"]
    )
    areas["flash"] = mult_rect(
        config["calibration.game_coords"], config["calibration.pct.flash"]
    )

    return areas, None
