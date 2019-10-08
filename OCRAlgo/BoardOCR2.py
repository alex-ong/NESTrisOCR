import numpy as np
from numba import njit
    
# atm this takes 12 millseconds to complete, with jit it takes <1ms.
# we want to eventually compile this numba AOT, so we don't need numba.

@njit('uint8[:,:](uint8[:,:,:],uint8[:],uint8[:])')
def parseImage2(img,color1,color2):

    black = np.array((10,10,10), dtype=np.uint8)
    white = np.array((240,240,240), dtype=np.uint8)
    
    colors = [black,white,color1,color2]
    
    result = np.zeros((20,10),dtype=np.uint8)
    
    for x in range(10):
        for y in range(20):
            pix = img[y,x]
            closest = 0
            lowest_dist = (256*256)*3
            i = 0
            for color in colors:
                dist = ((color[0] - pix[0]) * (color[0] - pix[0]) +
                       (color[1] - pix[1]) * (color[1] - pix[1]) +
                       (color[2] - pix[2]) * (color[2] - pix[2]))
                if dist < lowest_dist:
                    lowest_dist = dist
                    closest = i
                i += 1
                
            result[y,x] = closest
    
    return result
    
