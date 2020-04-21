def spawn_subimage(rect):
    # gets the 2x4 region out of the fieldPerc
    # return middle 4 / 10 x values and 2 / 20 y values
    tileX = rect[2] / 10.0
    tileY = rect[3] / 20.0
    return [rect[0] + tileX * 3, rect[1], tileX * 4, tileY * 2]
