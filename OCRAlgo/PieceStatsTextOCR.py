from lib import mult_rect


def generate_stats(captureCoords, statBoxPerc, statHeight, do_mult=True):
    statGap = (statBoxPerc[3] - (7 * statHeight)) / 6
    statGap = statGap + statHeight
    offsets = [i * (statGap) for i in range(7)]
    pieces = ["T", "J", "Z", "O", "S", "L", "I"]
    result = {}
    for i, piece in enumerate(pieces):
        offset = offsets[i]
        box = (statBoxPerc[0], statBoxPerc[1] + offset, statBoxPerc[2], statHeight)
        if do_mult:
            result[piece] = mult_rect(captureCoords, box)
        else:
            result[piece] = box
    return result
