import PIL
from PIL import Image, ImageEnhance

data = {}
redData = {}
digits = ['0','1','2','3','4','5','6','7','8','9','null']

MONO = True
IMAGE_SIZE = 7
BLOCK_SIZE = IMAGE_SIZE+1
IMAGE_MULT = 2

def setupColour(prefix, outputDict):
    #setup white digits
    for digit in digits:
        filename = prefix + str(digit) + '.png'
        if digit == 'null':
            filename = 'null.png'
        img = Image.open('../assets/' + filename)
        
        img = img.convert('L')
        if IMAGE_MULT != 1:
            img = img.resize((IMAGE_SIZE*IMAGE_MULT,
                              IMAGE_SIZE*IMAGE_MULT),PIL.Image.ANTIALIAS)
        outputDict[digit] = img.load()
        
def setupData():
    setupColour('sprite_templates/',data) #setup white
    setupColour('samples/red',redData) #setup red

def dist(col):
    return col*col
    
def sub(col1,col2):
    return col1-col2


def scoreDigit(img, startX, startY, red):
    scores = []
    template = redData if red else data
    for digit in digits:
        score = 0
        for y in range(IMAGE_SIZE*IMAGE_MULT):
            for x in range(IMAGE_SIZE*IMAGE_MULT):
                a = template[digit][x,y]
                b = img[startX+x,startY+y]
                score += dist(sub(a,b))
                
        scores.append((score, digit))
    scores.sort(key=lambda tup:tup[0])
    return scores[0]

#convert to black/white, with custom threshold    
def contrastImg(img):  
    if MONO:
        img = img.convert('L')    
    #img = ImageEnhance.Brightness(img).enhance(2.0) # hack to parse red
    #img = ImageEnhance.Contrast(img).enhance(3.0)
    #img = ImageEnhance.Sharpness(img).enhance(1.5)
    return img
    
def convertImg(img, count, show):
    img = contrastImg(img)        
    img = img.resize((((BLOCK_SIZE)*count-1)*IMAGE_MULT,
                        IMAGE_SIZE*IMAGE_MULT),PIL.Image.ANTIALIAS)
    if show:
        img.show()
    img = img.load()        
    return img    

def scoreImage(img, count, show=False, red=False):
    img = convertImg(img,count,show)
    label = ""
    for i in range(count):
        result = scoreDigit(img,i*(BLOCK_SIZE*IMAGE_MULT),0, red)
        if result[1] == 'null':
            return None
        else:
            label += result[1]
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
    