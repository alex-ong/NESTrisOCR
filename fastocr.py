import PIL
from PIL import Image, ImageEnhance

data = {}
digits = ['0','1','2','3','4','5','6','7','8','9','null']
MONO = True
def setupData():
    for digit in digits:
        data[digit] = Image.open(str(digit) + '.png')
        if MONO:
            data[digit] = data[digit].convert('L')
        data[digit] = data[digit].load()

        
if MONO:
    def dist(col):
        return col*col
        
    def sub(col1,col2):
        return col1-col2
else:
    def dist (col):
        return col[0]* col[0] + col[1]*col[1] + col[2]*col[2]


    def sub(col1,col2):
        return (col1[0] - col2[0],
                col1[1] - col2[1],
                col1[2] - col2[2])


def scoreDigit(img, startX, startY):
    scores = []
    
    for digit in digits:
        score = 0
        for y in range(7):
            for x in range(7):
                a = data[digit][x,y]
                b = img[startX+x,startY+y]
                score += dist(sub(a,b))
                
        scores.append((score, digit))
    scores.sort(key=lambda tup:tup[0])
    return scores[0]

#convert to black/white, with custom threshold    
def contrastImg(img):  
    if MONO:
        img = img.convert('L')    
    img = ImageEnhance.Sharpness(img).enhance(3.0)
    img = ImageEnhance.Brightness(img).enhance(2.0)
    img = ImageEnhance.Contrast(img).enhance(2.0)     
    
    return img
    
def convertImg(img, count,show):
    img = contrastImg(img)    
    if show:
        img.show()
    img = img.resize((8*count-1,7),PIL.Image.ANTIALIAS)
    
    img = img.load()        
    return img    

def scoreImage(img,count,show=False):
    img = convertImg(img,count,show)
    label = ""
    for i in range(count):
        result = scoreDigit(img,i*8,0)
        if result[1] == 'null':
            return None
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
    