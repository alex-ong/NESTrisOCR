from PIL import Image


# if we have board method we can analyse that
def parseBoard(board):
    return False


# otherwise we can analyse the color of a tile.
def parseImage(img, limit):
    img = img.resize((1, 1), Image.BOX)
    color1 = img.getpixel((0, 0))
    result = color1[0] > limit
    return result
