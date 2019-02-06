from PIL import Image
import PIL
data = {}
digits = ['0','1','2','3','4','5','6','7','8','9','null']
def setupData():
    for digit in digits:
        data[digit] = Image.open(str(digit) + '.png')
        data[digit] = threshImg(data[digit])
        data[digit] = data[digit].load()
        
        
'''
def dist (col):
    return col[0]* col[0] + col[1]*col[1] + col[2]*col[2]


def sub(col1,col2):
    return (col1[0] - col2[0],
            col1[1] - col2[1],
            col1[2] - col2[2])
'''
def dist(col):
    return col*col
    
def sub(col1,col2):
    return col1-col2
            
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
def threshImg(img):
    thresh = 20
    fn = lambda x : 255 if x > thresh else 0
    return img.convert('L').point(fn, mode='1')
    
def convertImg(img, count):
    img = threshImg(img)
    img = img.resize((8*count-1,7),PIL.Image.ANTIALIAS)
    img = img.load()        
    return img    

def scoreImage(img,count):
    img = convertImg(img,count)
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
    