from PIL import Image, ImageDraw
from enum import Enum

class InterlaceMode(Enum):
    NONE_NO_DOWNSCALE = 0
    NONE = 1
    DISCARD_TOP = 1
    DISCARD_BOTTOM = 2
    TOP_FIRST = 3
    BOTTOM_FIRST = 4

def deinterlace(img, mode=InterlaceMode.NONE):
    if mode == InterlaceMode.NONE_NO_DOWNSCALE:
        return (img, None)

    if mode == InterlaceMode.NONE:
        #first, downscale horizontally.
        size = list(img.size)
        size[0] //= 2
        size[1] //= 2
        img = img.resize(size, Image.NEAREST)
        return (img, None)

    #first, downscale horizontally.
    size = list(img.size)
    size[0] //= 2
    img = img.resize(size, Image.NEAREST)

    
    if mode != InterlaceMode.DISCARD_TOP:
        size[1] //= 2
        top = img.resize(size, Image.NEAREST) # NEAREST drops the lines
    else:
        top = None

    if mode != InterlaceMode.DISCARD_BOTTOM:
        bottom = img.crop([0,1,img.size[0],img.size[1]])
        img.paste(bottom)
        bottom = img.resize(size,Image.NEAREST)
        bottom_shift = bottom.crop([0,0,bottom.size[0],bottom.size[1]-1])
        bottom.paste(bottom_shift,(0,1))
        drawer = ImageDraw.Draw(bottom)
        drawer.rectangle([(0,0),(20,20)], fill= '#FF0000')
    else:
        bottom = None
    
    if mode == InterlaceMode.DISCARD_TOP:
        return (bottom, None)
    elif mode == InterlaceMode.DISCARD_BOTTOM:
        return (top, None)
    elif mode == InterlaceMode.TOP_FIRST:
        return (top, bottom)
    else:
        return (bottom, top)
