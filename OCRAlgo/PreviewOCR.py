from config import config
from lib import lerp

cached = []
cachedPPP = None
def calculateOffsets():
    baseRect = config.previewPerc
    global cachedPPP
    global cached
    if baseRect != cachedPPP:

        left, right, top, bottom = (baseRect[0],
                                    baseRect[0]+baseRect[2],
                                    baseRect[1],
                                    baseRect[1]+baseRect[3])
        p1 = (lerp(left,right,0.3),lerp(top,bottom,0.875))
        p2 = (lerp(left,right,0.4375),lerp(top,bottom,0.875))
        p3 = (lerp(left,right,0.6875),lerp(top,bottom,0.875))
        cached = [p1,p2,p3]
        cachedPPP = baseRect
        
    return cached

    
def parseImage(img):
    pass