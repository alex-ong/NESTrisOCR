CurPieceImageSize = (23, 12)

BLACK_LIMIT = 20

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


def luma(pixel):
    return pixel[0] * 0.299 + pixel[1] * 0.587 + pixel[2] * 0.114


def is_block_active(stage_img, x, y):
    # fastest, but perhaps not so accurate?
    _luma = luma(stage_img[x, y])
    return _luma > BLACK_LIMIT


def parseImage(img, colors):
    loaded_img = img.load()

    for name, blocks in CURRENT_PIECE_BLOCKS.items():
        detected = True

        for block in blocks:
            if not is_block_active(
                loaded_img, round(block[0] * img.width), round(block[1] * img.height)
            ):
                detected = False
                break

        if detected:
            return name
