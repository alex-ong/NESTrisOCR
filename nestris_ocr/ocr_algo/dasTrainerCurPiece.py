CurPieceImageSize = (23, 12)

CURRENT_PIECE_BLOCKS = {
    # Alignment 1
    "Z": ((0.140, 0.192), (0.462, 0.192), (0.462, 0.846), (0.769, 0.846)),
    "S": ((0.462, 0.192), (0.769, 0.192), (0.462, 0.846), (0.140, 0.846)),
    "T": ((0.140, 0.192), (0.462, 0.192), (0.769, 0.192), (0.462, 0.846)),
    # Alignment 2
    "L": ((0.140, 0.192), (0.462, 0.192), (0.731, 0.192), (0.140, 0.808)),
    "J": ((0.140, 0.192), (0.462, 0.192), (0.731, 0.192), (0.769, 0.808)),
    # Alignment 3
    "O": ((0.269, 0.231), (0.635, 0.231), (0.269, 0.846), (0.635, 0.846)),
    # Alignment 4
    "I": ((0.096, 0.538), (0.365, 0.538), (0.635, 0.538), (0.904, 0.538)),
}


def parseImage(img, colors):
    w = img.width
    h = img.height

    for name, blocks in CURRENT_PIECE_BLOCKS.items():
        detected = True

        for block in blocks:
            x = round(block[0] * w)
            y = round(block[1] * h)

            if colors.isBlack(img.getpixel((x, y))):
                detected = False
                break

        if detected:
            return name
