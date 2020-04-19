from config import config
from lib import mult_rect, screenPercToPixels, XYWHOffsetAndConvertToLTBR


def getWindowAreas():
    # gather list of all areas that need capturing
    # that will be used to determine the minimum window area to capture
    areas = {}
    areas["score"] = mult_rect(config.CAPTURE_COORDS, config.scorePerc)
    areas["lines"] = mult_rect(config.CAPTURE_COORDS, config.linesPerc)
    areas["level"] = mult_rect(config.CAPTURE_COORDS, config.levelPerc)
    areas["field"] = mult_rect(config.CAPTURE_COORDS, config.fieldPerc)
    areas["color1"] = mult_rect(config.CAPTURE_COORDS, config.color1Perc)
    areas["color2"] = mult_rect(config.CAPTURE_COORDS, config.color2Perc)
    areas["stats2"] = mult_rect(config.CAPTURE_COORDS, config.stats2Perc)
    areas["stats"] = mult_rect(config.CAPTURE_COORDS, config.statsPerc)
    areas["preview"] = mult_rect(config.CAPTURE_COORDS, config.previewPerc)
    areas["flash"] = mult_rect(config.CAPTURE_COORDS, config.flashPerc)

    coords_list = areas.values()

    return (areas, None)
