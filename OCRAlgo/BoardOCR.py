import PIL
import numpy as np

def parseImage(img, color1, color2):
    color1 = color1.resize((1,1), PIL.Image.ANTIALIAS)
    color1 = color1.getpixel((0,0))

    color2 = color2.resize((1,1), PIL.Image.ANTIALIAS)
    color2 = color2.getpixel((0,0))
    
    result = [[0] * 10 for i in range(20)]
    
    img = img.resize((10,20),PIL.Image.NEAREST)

    colors = [(25,25,25),(240,240,240),color1,color2]

    #todo: change to nparray to significantly speedup
    for x in range(10):
        for y in range(20):
            pix = img.getpixel((x,y))
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
    
