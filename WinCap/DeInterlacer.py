from PIL import Image
from enum import Enum

class InterlaceMode(Enum):
    NONE = 0
    DISCARD_ODD = 1
    DISCARD_EVEN = 2
    ODD_FIRST = 3
    EVEN_FIRST = 4

def deinterlace(img, mode=InterlaceMode.NONE):
    if mode == InterlaceMode.NONE:
        return (img, None)

    #first, downscale horizontally.
    size = list(img.size)
    size[0] //= 2
    img = img.resize(size, Image.NEAREST)

    
    if mode != InterlaceMode.DISCARD_EVEN:
        size[1] //= 2
        even = img.resize(size, Image.NEAREST) # NEAREST drops the lines
    else:
        even = None

    if mode != InterlaceMode.DISCARD_ODD:
        odd = img.crop([0,1,img.size[0],img.size[1]])
        img.paste(odd)
        odd = img.resize(size,Image.NEAREST)
    else:
        odd = None
    
    if mode == InterlaceMode.DISCARD_ODD:
        return (even, None)
    elif mode == InterlaceMode.DISCARD_EVEN:
        return (odd, None)
    elif mode == InterlaceMode.ODD_FIRST:
        return (odd, even)
    else:
        return (even, odd)
