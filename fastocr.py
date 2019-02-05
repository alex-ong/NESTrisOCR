from PIL import Image
import PIL
data = {}

def setupData():
    for i in range(10):
        data[i] = Image.open(str(i) + '.png')
        data[i] = data[i].load()
        
def dist (col):
    return col[0]* col[0] + col[1]*col[1] + col[2]*col[2]

def sub(col1,col2):
    return (col1[0] - col2[0],
            col1[1] - col2[1],
            col1[2] - col2[2])
            
def scoreDigit(img, startX, startY):
    scores = []
    for digit in range(10):
        score = 0
        for y in range(7):
            for x in range(7):
                a = data[digit][x,y]
                b = img[startX+x,startY+y]
                score += dist(sub(a,b))
                
        scores.append((score, digit))
    scores.sort(key=lambda tup:tup[0])
    
    return scores[0]
    
if __name__ == '__main__':
    setupData()
    import time
    
    t = time.time()
    for i in range(1):
        img = Image.open("test/"+"{:06d}".format(i*100)+".png")
        t2 = time.time()
        img = img.resize((47,7),PIL.Image.NEAREST)
        img = img.load()        
        label = ""
        for i in range(6):
            result = scoreDigit(img,i*8,0)
            label += str(result[1])
        
    print ("total time:", str(time.time() - t))
    print ("rescale time:", str(time.time() - t2))
    print ("AI time:", str(t2-t))
    