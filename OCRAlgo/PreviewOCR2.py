from PIL import Image, ImageEnhance
import numpy as np

cachedOffsets = []
cachedPPP = None

BLACK_LIMIT = 15
COUNT_PERC = 0.7
COUNT_PERC_O = 0.8


def isNotBlack(pixel):
    if pixel > BLACK_LIMIT:
        return 1
    else:
        return 0

isNotBlackVectorized = np.vectorize(isNotBlack)

#look at assets/doc for description
def parseImage(img):    
    img = img.resize((31,15),Image.BOX)    
    img = ImageEnhance.Contrast(img).enhance(3.0)
    img = img.convert('L')
    img = img.getdata()
    img = np.asarray(img)
    #img is in y,x format
    img = np.reshape(img,(15,-1))
    img = isNotBlackVectorized(img)
    
    #first, check for I and None
    i_pixels = np.sum(img[4:11,:4]) + np.sum(img[4:11,-4:]) #perfect score is 56.
    i_pixels = i_pixels >= int(56 * COUNT_PERC)
    
    if i_pixels:
        return "I"
    
    o_pixels_row1 = np.sum(img[:7,8:22]) #perfect score is 98
    o_pixels_row2 = np.sum(img[8:,8:22]) #perfect score is 98
    
    o_pixels = (o_pixels_row1 > int(98 * COUNT_PERC_O) and
                o_pixels_row2 > int(98 * COUNT_PERC_O))
    
    if o_pixels:
        return "O"

    #now we can simplify to 3x2 grid.
    grid = [[0,0,0], 
            [0,0,0]]
    for y in range(2):
        yStart = 8*y
        yEnd = yStart+7
        for x in range(3):
            xStart = 4+8*x
            xEnd = xStart+7
            grid[y][x] = np.sum(img[yStart:yEnd,xStart:xEnd]) > int(49*COUNT_PERC)
    
    if grid[0][0] and grid[0][1] and grid[0][2]: #j, t, l
        if grid[1][0]:
            return 'L'
        if grid[1][1]:
            return 'T'
        if grid[1][2]:
            return 'J'
        return None
    
    if not grid[0][0] and grid[0][1] and grid[0][2]:
        return 'S'
    
    if grid[0][0] and grid[0][1] and not grid[0][2]:
        return 'Z'
    
    return None
    
if __name__ == '__main__':
    #run this from parent directory as "python -m OCRAlgo.PreviewOCR2"
    img = Image.open('assets/test/s.png')
    import time
    t = time.time()
    for i in range(10000):
        parseImage(img)
    print (time.time() - t, (time.time() - t) / 10000)
    
    

