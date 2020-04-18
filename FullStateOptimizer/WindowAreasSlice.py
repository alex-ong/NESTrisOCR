from config import config
from lib import mult_rect, screenPercToPixels, XYWHOffsetAndConvertToLTBR

def getWindowAreas():
    # gather list of all areas that need capturing
    # that will be used to determine the minimum window area to capture
    areas = {}
    areas['score'] = mult_rect(config.CAPTURE_COORDS,config.scorePerc)
    areas['lines'] = mult_rect(config.CAPTURE_COORDS,config.linesPerc)
    areas['level'] = mult_rect(config.CAPTURE_COORDS,config.levelPerc)
    areas['field'] = mult_rect(config.CAPTURE_COORDS, config.fieldPerc)
    
    #Todo: config.color_method == DYNAMIC vs LOOKUP
    areas['color1'] = mult_rect(config.CAPTURE_COORDS, config.color1Perc)
    areas['color2'] = mult_rect(config.CAPTURE_COORDS, config.color2Perc)

    # Don't add all window_areas; only the ones we use.
    if config.capture_preview:
        areas['preview'] = mult_rect(config.CAPTURE_COORDS, config.previewPerc)
    if config.capture_stats:
        if config.stats_method == 'FIELD':
            areas['stats2'] = mult_rect(config.CAPTURE_COORDS, config.stats2Perc)
        if config.stats_method == 'TEXT':
            areas['stats'] = mult_rect(config.CAPTURE_COORDS, config.statsPerc)
    if config.flashMethod == 'BACKGROUND':
        areas['flash'] = mult_rect(config.CAPTURE_COORDS, config.flashPerc)

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
        minWindowAreaTLRB[3] - minWindowAreaTLRB[1]
    )

    # Extract offset from minimal capture area
    offset = minWindowAreaXYWH[:2]
    for key in areas:
        areas[key] = XYWHOffsetAndConvertToLTBR(offset, areas[key])
    
    return (areas, minWindowAreaXYWH)