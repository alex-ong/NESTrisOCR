import PIL
import numpy as np
import time
from numba import njit
   
def parseImage(img, color1, color2):    
    color1 = color1.resize((1,1), PIL.Image.ANTIALIAS)
    color1 = color1.getpixel((0,0))

    color2 = color2.resize((1,1), PIL.Image.ANTIALIAS)
    color2 = color2.getpixel((0,0))

    img = img.resize((10,20),PIL.Image.NEAREST)
    img = np.array(img,dtype=np.uint8)
    
    result = parseImage2(img,color1,color2)
    
    result2 = []
    for y in range(20):
        temp = "".join(str(result[y][x]) for x in range(10))        
        result2.append(temp)

    result = "".join(str(r) for r in result2)
    
    return result


# atm this takes 12 millseconds to complete, with jit it takes <1ms.
# we want to eventually compile this numba AOT, so we don't need numba.
@njit(cache=True)
def parseImage2(img,color1,color2):
    
    colors = [(10,10,10),(240,240,240),color1,color2]  
    
    result = [[0] * 10 for i in range(20)]
    
    for x in range(10):
        for y in range(20):
            pix = img[y,x]
            closest = 0
            lowest_dist = (256*256)*3
            for i, color in enumerate(colors):
                dist = ((color[0] - pix[0]) * (color[0] - pix[0]) +
                       (color[1] - pix[1]) * (color[1] - pix[1]) +
                       (color[2] - pix[2]) * (color[2] - pix[2]))
                if dist < lowest_dist:
                    lowest_dist = dist
                    closest = i
            result[y][x] = closest
    
    return result
    
    
if __name__ == '__main__':
    print(tester, len(''.join(tester)))
    print(compress_image(tester))
    print(len(compress_image(tester)))