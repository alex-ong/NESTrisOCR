import PIL
from PIL import Image, ImageEnhance
import time
try:
    import numpy as np
    NP_SUPPORTED = True
except:
    NP_SUPPORTED = False
    
import sys

data = {}
redData = {}
digits = ['0','1','2','3','4','5','6','7','8','9','null']
digitsLetters = digits + ['A','B','C','D','E','F']

MONO = True
IMAGE_SIZE = 7
BLOCK_SIZE = IMAGE_SIZE+1
IMAGE_MULT = 2
GAP = (BLOCK_SIZE - IMAGE_SIZE) * IMAGE_MULT

def setupColour(prefix, outputDict, digitList):
    #setup white digits
    for digit in digitList:
        filename = prefix + str(digit) + '.png'
        if digit == 'null':
            filename = 'sprite_templates/null.png'
        img = Image.open('assets/' + filename)
        
        img = img.convert('L')
        if IMAGE_MULT != 1:
            img = img.resize((IMAGE_SIZE*IMAGE_MULT,
                              IMAGE_SIZE*IMAGE_MULT),PIL.Image.ANTIALIAS)
        if NP_SUPPORTED:
            img = img.getdata()
            img = np.asarray(img)
            img = np.reshape(img, (IMAGE_SIZE * IMAGE_MULT, IMAGE_SIZE*IMAGE_MULT))
        else:
            img = img.load()

        outputDict[digit] = img
        
def setupData():
    setupColour('sprite_templates/', data, digitsLetters) #setup white
    setupColour('sprite_templates/red', redData, digits) #setup red


def getDigit(img, pattern, startX, startY, red):
    template = redData if red else data
    validDigits = digitsLetters if pattern == 'A' else digits

    if NP_SUPPORTED:
        scores = {}
        #img in y, x format
        subImage = img[:,startX:startX + 14]

        for digit in validDigits:
            diff = np.subtract(subImage, template[digit])
            diff = np.abs(diff)
            scores[digit] = np.sum(diff)

    else:
        scores = {digit:0 for digit in validDigits}
        MAX = IMAGE_SIZE * IMAGE_MULT

        for y in range(MAX):
            for x in range(MAX):
                b = img[startX + x, startY + y]

                for digit in digits:
                    a = template[digit][x, y]

                    sub = a - b
                    scores[digit] += sub * sub # adding distance

    lowest_score = float("inf")
    lowest_digit = None

    for digit, score in scores.items():
        if score < lowest_score:
            lowest_score = score
            lowest_digit = digit

    return lowest_digit

#convert to black/white, with custom threshold    
def contrastImg(img):  
    if MONO:
        img = img.convert('L')    
    #img = ImageEnhance.Brightness(img).enhance(2.0) # hack to parse red
    #img = ImageEnhance.Contrast(img).enhance(3.0)
    #img = ImageEnhance.Sharpness(img).enhance(1.5)
    return img
    
def convertImg(img, count, show):
    t = time.time()
    img = contrastImg(img)        
    img = img.resize((((BLOCK_SIZE)*count-1)*IMAGE_MULT,
                        IMAGE_SIZE*IMAGE_MULT),PIL.Image.ANTIALIAS)
    
    if show:
        img.show()
    
    if NP_SUPPORTED:
        img = img.getdata()
        img = np.asarray(img)
        #img is in y,x format
        img = np.reshape(img,(IMAGE_SIZE*IMAGE_MULT,-1))
    else:
        img = img.load()
    
    return img    


def scoreImage(img, digitPattern, show=False, red=False):
    count = len(digitPattern)
    img = convertImg(img,count,show)
    label = ""
    for (i, pattern) in enumerate(digitPattern):
        result = getDigit(img, pattern, i*(BLOCK_SIZE*IMAGE_MULT),0, red)
        if result == 'null':
            return None
        else:
            label += result
    return label

setupData()
    
if __name__ == '__main__':
    setupData()
    import time
    
    t = time.time()
    for i in range(1):
        img = Image.open("test/"+"{:06d}".format(i*100)+".png")
        
        
    print ("total time:", str(time.time() - t))
    print ("rescale time:", str(time.time() - t2))
    print ("AI time:", str(t2-t))
    